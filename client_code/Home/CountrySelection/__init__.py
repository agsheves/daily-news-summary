from ._anvil_designer import CountrySelectionTemplate
from anvil import *
import anvil.server

class CountrySelection(CountrySelectionTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    selected_country = self.country_dropDown.selected_value
    

    # Any code you write here will run before the form opens.

  def get_info_click(self, **event_args):
    """This method is called when the button is clicked"""
    anvil.server.call()
    pass

