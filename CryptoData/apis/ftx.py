import requests
import pandas as pd
import numpy as np
import time

END_POINT = 'https://ftx.com/api'

def request(request_code:str,params = None):
    time.sleep(0.02) # avoid to request so frequently
    url = END_POINT + request_code
    if params is None:
        response = requests.get(url).json()
    else:
        response = requests.get(url,params).json()
    if not response['success']:
        raise Exception(f'Failed to get data from the api.\n{response}')
    return response

# main functions

def get_all_spots():
    request_code = '/markets'
    response = request(request_code)
    markets = response['result']
    filterFunction = lambda x:'PERP' not in x['name'] and '1230' not in x['name'] and '0331' not in x['name'] and '2021' not in x['name'] and '2022' not in x['name'] and '2023' not in x['name']
    all_spots = [i['name'] for i in list(filter(filterFunction, markets))]
    return all_spots

def get_all_perp():
    request_code = '/markets'
    response = request(request_code)
    markets = response['result']
    '''
    markets = [
        {'name':'BTC-PERP',...},{'name':'BTC/USDT',...},...
    ]
    '''
    all_perp = [i['name'] for i in list(filter(lambda x: 'PERP' in x['name'], markets))]
    return all_perp

def get_price(symbol:str,resolution:int,start_time = None,end_time = None):
    '''
    parameters
    resolution: window length in seconds. options: 15, 60, 300, 900, 3600, 14400, 86400, or any multiple of 86400 up to 30*86400
    start_time: int ex.1543435435
    end_time: int
    '''
    request_code = f'/markets/{symbol}/candles?resolution={resolution}'
    params = {'market_name':symbol,
              'resolution':resolution,
              'start_time':start_time,
              'end_time':end_time}
    response = request(request_code,params = params)
    return response['result']

def get_funding_rate(symbol = None,start_time = None,end_time = None):
    params = {'start_time':start_time,
              'end_time':end_time,
              'future':symbol}
    request_code = '/funding_rates'
    response = request(request_code,params = params)
    return response['result']

def get_future_stats(symbol):
    request_code = f'/futures/{symbol}/stats'
    response = request(request_code)
    return response['result']

def get_trades(symbol,start_time = None,end_time = None):
    request_code = f'/markets/{symbol}/trades'
    params = {'market_name':symbol,
              'start_time':start_time,
              'end_time':end_time}
    response = request(request_code,params=params)
    return response['result']


def get_orderbook(symbol,depth = 1):
    request_code = f'/markets/{symbol}/orderbook?depth={depth}'
    response = request(request_code)
    return response['result']