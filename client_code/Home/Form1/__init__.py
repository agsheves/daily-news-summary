from ._anvil_designer import Form1Template
from anvil import *
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files

class Form1(Form1Template):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.

  def get_stories_click(self, **event_args):
    """This method is called when the button is clicked"""
    articles = anvil.server.call('get_risk_articles_newscatcher')
    self.unformatted_stories.text = articles
    pass

  def summrize_stories_click(self, **event_args):
    """This method is called when the button is clicked"""
    articles = self.unformatted_stories.text
    summaries = anvil.server.call('summarize_stories', articles)
    self.html_summaries.text = summaries
    pass

  def send_email_click(self, **event_args):
    stories = self.html_summaries.text
    status_message = anvil.server.call('send_daily_news_email', stories)
    self.email_result.text = status_message
    """This method is called when the button is clicked"""
    pass







