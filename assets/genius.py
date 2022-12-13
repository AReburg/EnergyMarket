import dash
import logging
import time
import json
import requests
import pandas as pd
from pandas import json_normalize
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
class ApiError(Exception):
    pass

"""
https://tradingeconomics.com/commodity/eu-natural-gas
"""

f = open('historic.json')
data = json.load(f)
data = data['series'][0]['data']
print(data[0])

df = json_normalize(data)
df['date'] = pd.to_datetime(df['date'], infer_datetime_format=True) #, format='%Y-%m%d:%H:%M:%S.%f')

df = df.iloc[-200:-1, 0:-1]
print(df.head())
print(df.columns)
f.close()


fig = go.Figure(data=[go.Candlestick(x=df["date"], open=df["open"], high=df["high"],
                low=df["low"], close=df["close"])])
fig.update(layout_xaxis_rangeslider_visible=False)
fig.show()