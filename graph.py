'Graph data, currently only graphs polymarket timeseries data, soon will add betfair data'

import plotly.express as px
import pandas as pd
import json


price_history = {}
with open('data/price_history.json', 'r') as f:
    price_history = json.load(f)


# Sample data
org_price_data = price_history['67801272423404117155322617512654122993764547063793027409355574196945307332941']
price_data = {}
for i in org_price_data:
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