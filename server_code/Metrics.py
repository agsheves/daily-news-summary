import anvil.google.auth, anvil.google.drive, anvil.google.mail
from anvil.google.drive import app_files
import anvil.email
import anvil.secrets
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta



##AlphaVantage API for API calls.
alphaVantageAPI = anvil.secrets.get_secret('alphaVantage')

import pandas as pd
import requests


#Get the required data from AlphaVantage
#Clean up the data and analyse it for low / average / high description
#Get a trend result
#Call the function and pass the commodity name and endpoint URL
#Endpoints:
#Wheat https://www.alphavantage.co/query?function=WHEAT&interval=monthly
#Oil (WTI) https://www.alphavantage.co/query?function=WTI&interval=monthly
@anvil.server.callable
def get_commodity_price_AlphaVantage(commodity_name, endpoint_url):
  url = f'{endpoint_url}&apikey={alphaVantageAPI}'
  r = requests.get(url)
  commodity_data = r.json()

  # convert the data to a dataframe
  commodity_df = pd.DataFrame(commodity_data['data'])

  # convert the 'date' column to datetime
  commodity_df['date'] = pd.to_datetime(commodity_df['date'])

  # sort by date and reset index
  commodity_df = commodity_df.sort_values('date').reset_index(drop=True)

  # convert 'value' column to float
  # First, coerce any errors during the conversion process, which will replace problematic values with NaN
  commodity_df['value'] = pd.to_numeric(commodity_df['value'], errors='coerce')

  # Then, if necessary, remove or fill any NaN values
  commodity_df = commodity_df.dropna(subset=['value'])
  # Or replace NaNs with the mean or median, for example
  # commodity_df['value'].fillna(commodity_df['value'].mean(), inplace=True)
  
  # filter to the last 18 months
  commodity_df_18 = commodity_df[commodity_df['date'] > commodity_df['date'].max() - pd.DateOffset(months=18)]

  # Get the high, low, and current prices
  high = commodity_df_18['value'].max()
  low = commodity_df_18['value'].min()
  current = commodity_df_18.loc[commodity_df_18['date'].idxmax(), 'value']

  # Get the mean and standard deviation
  mean = commodity_df_18['value'].mean()
  std = commodity_df_18['value'].std()

  # Determine current price status based on the mean and standard deviation
  if current < (mean - std):
    current_relative_price = "very low"
  elif current < mean:
    current_relative_price = "low"
  elif (current >= mean - 0.5*std) and (current <= mean + 0.5*std):
    current_relative_price = "around average"
  elif current <= (mean + std):
    current_relative_price = "high"
  else:
    current_relative_price = "very high"

  # Determine the 3-month trend
  three_month_trend = (commodity_df_18['value'].tail(1).values[0] - commodity_df_18['value'].tail(3).head(1).values[0]) / commodity_df_18['value'].tail(3).head(1).values[0]

  if three_month_trend > 0:
    current_commodity_trend = "upwards"
  elif three_month_trend < 0:
    current_commodity_trend = "downwards"
  else:
    current_commodity_trend = "relatively stable"

  # Return current commodity price and trend as a dictionary
  return {"Commodity": commodity_name, "Current Price ($)": current, "Current Relative Price (18-month window)": current_relative_price, "Current Trend (3-Month Window)": current_commodity_trend}


##Get all market data
@anvil.server.callable
def get_market_metrics():
  market_metrics = {}
  market_metrics["oil"] = anvil.server.call('get_commodity_price_AlphaVantage', 'Oil \(WTI\)', 'https://www.alphavantage.co/query?function=WTI&interval=monthly')
  market_metrics["wheat"] = anvil.server.call('get_commodity_price_AlphaVantage', 'wheat', 'https://www.alphavantage.co/query?function=WHEAT&interval=monthly')
  return market_metrics
  
#Write current metrics summary
@anvil.server.callable
def write_market_metrics_summary():
  market_metrics = anvil.server.call('get_market_metrics')
  # Extract commodity metrics
  wheat_current_trend = market_metrics["wheat"]["Current Trend (3-Month Window)"]
  wheat_relative_price = market_metrics["wheat"]["Current Relative Price (18-month window)"]
  wheat_current_price = market_metrics["wheat"]["Current Price ($)"]
  oil_current_trend = market_metrics["oil"]["Current Trend (3-Month Window)"]
  oil_relative_price = market_metrics["oil"]["Current Relative Price (18-month window)"]
  oil_current_price = market_metrics["oil"]["Current Price ($)"]
  # Create the body of the email
  metrics_summary = f"""

<p>Here are the current values for the tracked metrics:</p>

<h2><b>Wheat:</h2></b><br/><p>
- Current price: ${wheat_current_price}. This is {wheat_relative_price} for this 18-month period.<br/>
- The 3-month trend is {wheat_current_trend}</p>
<hr>
<h2><b>Oil:</h2></b><br/><p>
- Current price: ${oil_current_price}. This is {oil_relative_price} for this 18-month period.<br/>
- The 3-month trend is {oil_current_trend}</p>
<hr>
"""
  return metrics_summary


##############################################
#Emails the market metrics summaries
@anvil.server.callable()
def send_daily_metrics_email():
    try:
        today = datetime.now()
        date = (today.strftime("%d-%B-%Y"))
        day = (today.strftime("%A"))
        metrics_summary = anvil.server.call('write_market_metrics_summary')

        # email header and footer
        header = f"""
            <html>
            <body>
            <h2>Happy {day}! Here's the critical metrics for {date}</h2>
        """

        footer = """
            <p>That's it for today. See you tomorrow</p>
            <p><i>~Andrew</i></p>
            </body>
            </html>
        """

        daily_subject = (f"Critical metrics for {date}")

        mail_message_body = header + metrics_summary + footer  # this is an HTML message

        # Send Email
        anvil.email.send(to='andrew@andrewsheves.com',
                         subject=daily_subject,
                         html=mail_message_body,
                         from_address='andrew@tarjumansolutions.com',
                         from_name='Andrew')

        return "Email sent successfully."
    except Exception as e:
        return f"Failed to send email: {e}"
