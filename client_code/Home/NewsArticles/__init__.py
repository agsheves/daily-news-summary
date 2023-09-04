from ._anvil_designer import NewsArticlesTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from datetime import datetime, timedelta


class NewsArticles(NewsArticlesTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    stories = app_tables.newssummaries.search()
    self.repeating_panel_1.items = stories

    # Any code you write here will run before the form opens.
