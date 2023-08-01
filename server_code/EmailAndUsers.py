import anvil.users
import anvil.google.auth, anvil.google.drive, anvil.google.mail
from anvil.google.drive import app_files
import anvil.email
import anvil.secrets
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
from datetime import datetime, timedelta

#Archives the news for that day to leave a clean sheet for the next day's news
@anvil.server.callable
def archive_news():
    # Open your Google Sheet
    db = app_files.newslitfeed

    # Get the worksheets
    feed_ws = db["NewsLitFeed"]
    archive_ws = db["NewsLitArchive"]

    # Ensure there are more than just header rows in the feed
    if len(feed_ws.rows) > 1:
        # Get a list of all rows except for the first one (headers)
        rows_to_archive = feed_ws.rows[1:]

        # Iterate over each row in the list
        for row in rows_to_archive:
            # Copy row to archive worksheet
            archive_ws.add_row(**row)
  

        # Now that the rows are archived, delete them from the feed worksheet
        for row in rows_to_archive:
            row.delete()



@anvil.server.background_task
def send_full_daily_summary():
    try:
        today = datetime.now()
        date = (today.strftime("%d-%B-%Y"))
        day = (today.strftime("%A"))
        #articles = anvil.server.call('get_risk_articles_newscatcher')
        #split_articles_list = anvil.server.call('split_articles', articles)
        # Generate summaries
        #summaries = []
        #for chunk in split_articles_list:
            #summary = anvil.server.call('summarize_stories', chunk)
            #summaries.append(summary)
        # Join all summaries into one string
        #news_summary = ''.join(summaries)
        news_summary = anvil.server.call('get_risknews_newLit')
        metrics_summary = anvil.server.call('write_market_metrics_summary')

        # email header and footer
        header = f"""
        <html>
        <body>
        <p>Happy {day}! Here's your risk news summary for {date}.  As always, the key metrics we're tracking are at the bottom of the message.</p>
        """

        footer = """
        <p>That's it for today. See you tomorrow</p>
        <p><i>~Andrew</i></p>
        </body>
        </html>
        """

        daily_subject = (f"Risk news summary for {date}.")

        mail_message_body = header + news_summary + metrics_summary + footer  # this is an HTML message

        # Send Email
        anvil.email.send(to='andrew@andrewsheves.com',
                         subject=daily_subject,
                         html=mail_message_body,
                         from_address='andrew@tarjumansolutions.com',
                         from_name='Andrew')

        return "Email sent successfully."
        anvil.server.call('archive_news')
    except Exception as e:
        return f"Failed to send email: {e}"
