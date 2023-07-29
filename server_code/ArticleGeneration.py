import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.google.auth, anvil.google.drive, anvil.google.mail
from anvil.google.drive import app_files
import anvil.email
import anvil.server
import requests
import json
from datetime import datetime, timedelta
import anvil.secrets
import openai

##############################################
#Calls the WorldNews API and requests stories
#API reference is here https://worldnewsapi.com/
@anvil.server.callable
def get_risk_articles():
    def search_news(api_key, text, number=10, language='en', sort='publish-time', sort_direction='DESC'):
        url = "https://api.worldnewsapi.com/search-news"
        query = {
            'api-key': api_key,
            'text': text,
            'number': number,
            'language': language,
            'sort': sort,
            'sort-direction': sort_direction
        }
        response = requests.get(url, params=query)

        # Check if request was successful
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Request failed with status code {response.status_code}")
            return None

    api_key = anvil.secrets.get_secret('newsapi_key')  # Fetch API key from Anvil's Secret Service

    # Set your date constraint
    three_day_ago = datetime.now() - timedelta(days=3)

    # Call the API without the date constraint
    risk_news = search_news(api_key, "risk management" or "crisis management" or "crisis" or "cyber" or "compliance" or "governance", number=50)
    print(risk_news)

    risk_articles_list = []
    for news in risk_news['news']:
        # Get the article's publication date
        publish_date_str = news['publish_date']
        publish_date = datetime.strptime(publish_date_str, '%Y-%m-%d %H:%M:%S')

        # Check if the publication date falls within the last three days
        if publish_date >= three_day_ago:
            title = news['title']
            summary = news['text']
            link = news['url']
            source = news['source_country']  # Assuming this is the equivalent of 'rights'
            date = news['publish_date']  # The new API does not provide publish date

            risk_articles_list.append({
                'Headline': title,
                'Source': source,
                'Date': date,
                'Summary': summary,
                'Link': link,
            })

    return risk_articles_list


#######
#Calls the Newsdata.io API and requests stories
#API reference is here https://newsdata.io/

@anvil.server.callable
def get_risk_articles_newsdata():
    def search_news(api_key, text, number=10, language='en'):
        url = "https://newsdata.io/api/1/news"
        categories = "business"
        query = {
            'apikey': api_key,
            'qInTitle': text,
            'category': categories,
            'language': language
        }
        response = requests.get(url, params=query)

        # Check if request was successful
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Request failed with status code {response.status_code}")
            return None

    api_key = anvil.secrets.get_secret('newsData_key')  # Fetch API key from Anvil's Secret Service

    # Call the API with the keywords
    risk_news = search_news(api_key, "risk management OR crisis management OR crisis OR cyber OR compliance OR governance", number=50)

    if not risk_news or 'results' not in risk_news:
        return []

    risk_articles_list = []
    for news in risk_news['results']:
        title = news['title']
        summary = news['description'] 
        link = news['link']
        source = news.get('creator', 'Unknown')  # Use 'creator' as the source; if not present, use 'Unknown'

        risk_articles_list.append({
            'Headline': title,
            'Source': source,
            'Summary': summary,
            'Link': link,
        })

    return risk_articles_list

##Calls the NewsCatcher API

@anvil.server.callable
def get_risk_articles_newscatcher():
  newsCatcher_API = anvil.secrets.get_secret('newsCatcher_API')  # Fetch API key from Anvil's Secret Service

  # Set your date constraint
  three_day_ago = datetime.now() - timedelta(days=3)
  
  # Set your query parameters
  querystring = {"q":"risk management OR crisis management OR crisis OR cyber OR compliance OR governance",
                 "lang":"en",
                 "from": three_day_ago.strftime('%Y-%m-%d'),
                 "page_size":50}

  headers = {"x-api-key": newsCatcher_API}

  response = requests.request("GET", 'https://api.newscatcherapi.com/v2/search', headers=headers, params=querystring)
  
  risk_news = response.json()
  return risk_news

  risk_articles_list = []
  for article in risk_news['articles']:
    title = article['title']
    if 'photo' not in title.lower():
        if article['topic'] in topics:
            date = article['published_date']
            source = article['rights']
            summary = article['summary']
            link = article['link']
            topic = article['topic']

            risk_articles_list.append({
                'Headline': title,
                'Source': source,
                'Date': date,
                'Summary': summary,
                'Link': link,
            })

    risk_articles_str = json.dumps(risk_articles_list, indent=4)
    print(f'*********************\nHeadline: {title}\nSource: {source}\nTopic: {topic}\nDate: {date}\nSummary: {summary}\nLink to article: {link}\n\n')

##############################################
#Splits the articles up so these don't exceed the token count for the model. Using 15K as a limit.
@anvil.server.callable
def split_articles(articles, max_tokens=15000):
    # This is a simple function to split the list of articles into smaller chunks that will fit within the token limit.

    split_articles = []
    current_chunk = []
    current_tokens = 0

    for article in articles:
        # Calculate the number of tokens in this article.
        # This is a rough estimate, you might need to adjust it.
        # Here, I'm assuming an average of 5 tokens per word.
        article_tokens = len(article['Headline'].split()) + len(article['Summary'].split()) * 5

        # If adding this article would exceed the token limit, start a new chunk.
        if current_tokens + article_tokens > max_tokens:
            split_articles.append(current_chunk)
            current_chunk = []
            current_tokens = 0

        # Add the article to the current chunk and update the token count.
        current_chunk.append(article)
        current_tokens += article_tokens

    # Add the last chunk if it's not empty.
    if current_chunk:
        split_articles.append(current_chunk)
    return split_articles

##############################################
#Sends the stories to ChatGPT to summarize and put into HTML format
@anvil.server.callable
def summarize_stories(risk_articles_str):
    openai.api_key = anvil.secrets.get_secret('openai_api')

    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-16k",
        messages=[
          {"role": "system", "content": "You are an experienced risk and security analyst, responsible for writing succinct summary reports."},
          {"role": "user", "content": f"Please summarize these articles for a daily briefing email to help the reader understand each story. For each story, use the following format: Begin with an HTML <h1> tag for the headline. Follow this with the date in a new line. Then, summarize the story in a paragraph, ensuring the summary is concise yet informative. Conclude each story with a HTML <a> tag for the clickable source link where the link text is the source name. The articles should be separated by a horizontal line. Ignore articles that have no political, economic, security or geopolitical relevance. Return the results in HTML format to help formatting in Google Docs. Here are the articles: \n{risk_articles_str}"}
]

    )

    html_summary = completion.choices[0].message['content']
    return html_summary


##############################################
#Emails the news summaries
@anvil.server.callable()
def send_daily_news_email(html_summary):
    try:
        today = datetime.now()
        date = (today.strftime("%d-%B-%Y"))
        day = (today.strftime("%A"))

        # email header and footer
        header = f"""
            <html>
            <body>
            <h2>Happy {day}! Here's the risk news for {date}</h2>
        """

        footer = """
            <p>That's it for today. See you tomorrow</p>
            <p><i>~Andrew</i></p>
            </body>
            </html>
        """

        daily_subject = (f"Daily risk news for {date}")

        mail_message_body = header + html_summary + footer  # this is an HTML message

        # Send Email
        anvil.email.send(to='andrew@andrewsheves.com',
                         subject=daily_subject,
                         html=mail_message_body,
                         from_address='andrew@tarjumansolutions.com',
                         from_name='Andrew')

        return "Email sent successfully."
    except Exception as e:
        return f"Failed to send email: {e}"
  

@anvil.server.background_task
def send_daily_risk_summary():
    articles = get_risk_articles()  # Call the function directly
    split_articles_list = split_articles(articles)
    # Generate summaries
    summaries = []
    for chunk in split_articles_list:
        summary = summarize_stories(chunk)
        summaries.append(summary)
    # Join all summaries into one string
    full_summary = ''.join(summaries)

    # Now you can pass 'full_summary' to your 'send_daily_news_email' function
    send_daily_news_email(full_summary)

