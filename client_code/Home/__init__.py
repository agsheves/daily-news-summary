from ._anvil_designer import HomeTemplate
from .NewsArticles import NewsArticles
from anvil import *
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.server
import anvil.js


class Home(HomeTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.

  def show_news_button_click(self, **event_args):
    """This method is called when the button is clicked"""
    alert(
      title='Latest news',
      large=True,
      contents = NewsArticles()
    )
    pass

