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
            <h2>Happy {day}! Here's your daily summary for {date}</h2>
        """

        footer = """
            <p>That's it for today. See you tomorrow</p>
            <p><i>~Andrew</i></p>
            </body>
            </html>
        """

        daily_subject = (f"Daily summary for {date}")

        mail_message_body = header + news_summary + metrics_summary + footer  # this is an HTML message

        # Send Email
        anvil.email.send(to='andrew@andrewsheves.com',
                         subject=daily_subject,
                         html=mail_message_body,
                         from_address='andrew@tarjumansolutions.com',
                         from_name='Andrew')

        return "Email sent successfully."
    except Exception as e:
        return f"Failed to send email: {e}"
