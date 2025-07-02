'''
get any market info by the slug of the market found in the url
https://gamma-api.polymarket.com/events?slug=event_slug
https://gamma-api.polymarket.com/markets?slug=market_slug

Graph data of any market
'''
from py_clob_client.client import ClobClient
from datetime import datetime, timedelta
import requests, json, aiohttp, asyncio, time
import plotly.express as px
import pandas as pd
import json

host = "https://clob.polymarket.com"
client = ClobClient(host)
gamma = "https://gamma-api.polymarket.com/" 
clob = "https://clob.polymarket.com/"
# eleven_hours_ago = datetime.now() - timedelta(hours=11)
start = 1733281200
end = datetime.timestamp(datetime.fromtimestamp(start) + timedelta(hours=4))
params = {
    #clob token ID yayyy  (can find using gamma api + url slug)
    'market' : '97670620555248231323772737427234059075713336387077218979048997260701707773312',
    'startTs' : start,
    'endTs' : end,
    # 'interval' : '1d',
    'fidelity' : '1'
}
print(params)
price_history = requests.get(clob+"prices-history", params=params).json()['history']




#graph this shit
price_data = {}
for i in price_history:
    price_data[int(i['t'])] = float(i['p'])

# Convert dictionary to list of (timestamp, price) tuples
data = [(t, p) for t, p in price_data.items()]
# Create DataFrame from the list of tuples
df = pd.DataFrame(data, columns=['timestamp', 'price'])
# Convert timestamp to datetime
df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')

# Create the line plot using Plotly Express
fig = px.line(df, x='timestamp', y='price', title='Price Over Time', markers=True)  
fig.update_layout(dragmode='pan')
fig.update_xaxes(range=[df['timestamp'].min(), df['timestamp'].max()])
fig.update_yaxes(range=[0, 1])

fig.show(config=dict({'scrollZoom': True}))