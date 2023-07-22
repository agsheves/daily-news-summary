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
    three_days_ago = datetime.now() - timedelta(days=3)

    # Call the API without the date constraint
    risk_news = search_news(api_key, "risk management" or "crisis management" or "crisis" or "cyber" or "compliance" or "governance", number=50)

    risk_articles_list = []
    for news in risk_news['news']:
        # Get the article's publication date
        publish_date_str = news['publish_date']
        publish_date = datetime.strptime(publish_date_str, '%Y-%m-%d %H:%M:%S')

        # Check if the publication date falls within the last three days
        if publish_date >= three_days_ago:
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


@anvil.server.callable
def summarize_stories(risk_articles_str):
    openai.api_key = anvil.secrets.get_secret('openai_api')

    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-16k",
        messages=[
            {"role": "system", "content": "You are an experienced risk and security analyst, responsible for writing succinct summary reports."},
            {"role": "user", "content": f"Please summarize these articles for a daily briefing email to help the reader understand each story. Include a headline for each story and start the summary on a seperate line. Ignore articles that have no political, economic, security or geopolitical relevance. Use the source links for each story to include clickable link for each story from a reputable news source where the link text is the source name. Return the results in HTML format to help formatting in Google Docs. Here are the articles: \n{risk_articles_str}"}
        ]
    )

    html_summary = completion.choices[0].message['content']
    return html_summary

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

@anvil.server.callable
def store_news():
  

@anvil.server.background_task
def send_daily_risk_summary():
  articles = get_risk_articles()  # Call the function directly
  summary = summarize_stories(articles)
  send_daily_news_email(summary)
