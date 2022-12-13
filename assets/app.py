import dash
import logging
import time
import json
import requests
"""
Documentation: https://www.commodities-api.com/documentation#historicalrates
"""
class ApiError(Exception):
    pass
start_date = "2021-05-01"
end_date = "2020-05-25"

base_currency = 'TGZ22'
symbol = 'EUR'
endpoint = 'latest'
access_API = 'ns8db94qwty8z0d3qtjd831aytoys40jnnz2e814c0hwft056uy0sgfjwyfi'

urls = f"https://www.commodities-api.com/api/{endpoint}?access_key={access_API}&base={base_currency}\
&symbols={symbol}"
resp = requests.get(urls)
print(urls)
# time series
#resp = requests.get(f"https://www.commodities-api.com/api/timeseries?access_key={access_API}&start_date={start_date}&end_date={end_date}&base={base_currency}\
#&symbols={symbol}")
# high low
start_date = "2022-11-08"
url = f"https://www.commodities-api.com/api/open-high-low-close/{start_date}?access_key={access_API}&base=TGZ22&symbols=EUR"
resp = requests.get(url)
if resp.status_code != 200:
    raise ApiError("Test")

print(resp.text)
print(url)