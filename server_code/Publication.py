import anvil.users
import anvil.google.auth, anvil.google.drive, anvil.google.mail
from anvil.google.drive import app_files
import anvil.email
import anvil.secrets
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
import anvil.http
from datetime import datetime

@anvil.server.callable
def send_risk_news_to_zapier():
    try:
        # Your HTML content
        news_summary = anvil.server.call('get_risknews_newLit')
        metrics_summary = anvil.server.call('write_market_metrics_summary')
        today = datetime.today()
        date_str = (today.strftime("%d %B %Y"))
        day_str = (today.strftime("%A"))

        # Construct the content to send
        content = f"""
        <html>
        <body>
        {news_summary}
        {metrics_summary}
        </body>
        </html>
        """

        # Send the content to the Zapier webhook
        response = anvil.http.request(
            url='https://hooks.zapier.com/hooks/catch/1839647/31la39u/',
            method='POST',
            data={
              'content': content,
              'date': date_str,
              'day': day_str
            },
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
        )

        return "Data sent successfully to Zapier."

    except Exception as e:
        return f"Failed to send data to Zapier: {e}"
