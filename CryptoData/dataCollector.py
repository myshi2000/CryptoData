import json
import time
import pandas as pd
import numpy as np
import datetime as datetime
from apis import ftx

def transfer_time(times:str,timeZone = 8) -> int:
    try:
        timeArray = time.strptime(times,'%Y-%m-%dT%H:%M:%S.%f+00:00')
    except ValueError:
        timeArray = time.strptime(times,'%Y-%m-%dT%H:%M:%S+00:00')
    ts = int(time.mktime(timeArray)) + 3600 * timeZone
    return ts

class FtxData():
    def __init__(self):
        self.DataRestriction = 400 # get no more than 400 lines of data from the api every time
        self.spots = ftx.get_all_spots()
        self.futures = ftx.get_all_perp()
        self.filepath = None

    def set_filepath(self,path):
        self.filepath = path


    def getLastTrade(self,symbol,timestamp:int):
        trades = ftx.get_trades(symbol,start_time = timestamp - 50,end_time = timestamp + 50)
        trades.reverse()
        price = None
        side = None
        for trade in trades:
            t = transfer_time(trade['time'])
            if t > timestamp:
                side = trade['side']
                price = trade['price']
        return side, price

    def getBidAsk1(self,symbol):
        orderbook = ftx.get_orderbook(symbol)
        bid1 = orderbook['bids'][0][0]
        ask1 = orderbook['asks'][0][0]
        return bid1,ask1

    def get_spots_data(self,symbol,resolution,start_time,end_time):
        timeblock = self.DataRestriction * resolution
        data = []
        for t0 in range(start_time,end_time,timeblock):
            historical_data = ftx.get_price(symbol,resolution,t0,min(end_time, t0 + timeblock))
            data = data + historical_data
            print(f'{len(data)} hours basic data collected.',end = '\r')
        print()

        if len(data) == 0:
            return pd.DataFrame()
        df = pd.DataFrame(data)
        df.index = df['startTime']
        df = df.drop('startTime',axis = 1)

        df['time'] = df['time']/1000
        return df

    def get_futures_data(self,symbol,resolution,start_time,end_time):
        timeblock = self.DataRestriction * resolution
        historical_data,funding_rate_data = [],[]

        for t0 in range(start_time,end_time,timeblock):
            data1 = ftx.get_price(symbol,resolution,t0,min(end_time, t0 + timeblock))
            data2 = ftx.get_funding_rate(symbol,t0,min(end_time, t0 + timeblock))

            historical_data = historical_data + data1
            funding_rate_data = funding_rate_data + data2

            print(f'{len(historical_data)} hours basic data collected.',end = '\r')
        print()

        df1 = pd.DataFrame(historical_data)
        df1.index = df1['startTime']
        df1 = df1.drop('startTime',axis = 1)

        df2 = pd.DataFrame(funding_rate_data)
        df2.index = df2['time']
        df2 = df2.drop('time',axis = 1)

        df = pd.merge(df1, df2, left_index=True, right_index=True)
        #df = pd.concat([df1,df2],axis=1)

        df['time'] = df['time']/1000
        return df

    def get_spread(self,symbols,timespread = 3600): # collect currenct data in timespread seconds
        symbols_data = dict() # store the data here
        for symbol in symbols:
            symbols_data[symbol] = []

        t0 = time.time()
        count = 0
        while True:
            t1 = time.time()
            if t1 - t0 > timespread:
                break
            for symbol in symbols:
                try:
                    t_i = time.time()
                    bid1,ask1 = self.getBidAsk1(symbol)
                    data_i = {'symbol':symbol,'timestamp':t_i,'bid1':bid1,'ask1':ask1}
                    symbols_data[symbol].append(data_i)
                except Exception:
                    pass
            count += 1
            if count%1 == 0:
                print(f'{count} data collected.',end='\r')
            time.sleep(0.1)

        # save the data
        for symbol in symbols:
            df = pd.DataFrame(symbols_data[symbol])
            name = symbol[:]
            name = name.replace('/','-')
            df.to_csv(f'{self.filepath}\{name}.csv')
