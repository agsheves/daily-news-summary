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
        stories = app_tables.newssummaries.search(
            tables.order_by("dateTimeAdded", ascending=False)
        )
        self.init_components(**properties)
        self.repeating_panel_1.items = stories
        print("NewsArticles form initialized")

