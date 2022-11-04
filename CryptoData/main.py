import pandas as pd
import numpy as np
from dataCollector import FtxData
import time

# set parameters here
PATH = 'path' # the path to store your file. please use different path when collecting different kinds of data
START_TIME = 1570194000
END_TIME = 1667281098

# Initialize
data = FtxData()
data.set_filepath(PATH)

# get spots data
count = 0
for spot in data.spots:
    try:
        print(f'[{spot}] collecting.')
        df = data.get_spots_data(spot,resolution = 3600,start_time=START_TIME,end_time=END_TIME)
        name = spot[:]
        name = name.replace('/','-')
        df.to_csv(f'{data.filepath}\{name}.csv')
        print(f'[{spot}] finished.')
        count += 1
        print(f'{count} of {len(data.spots)}\n')
    except Exception:
        pass

# get futures data
count = 0
for future in data.futures:
    try:
        print(f'[{future}] collecting.')
        count += 1
        df = data.get_futures_data(future,resolution = 3600,start_time=START_TIME,end_time=END_TIME)
        df.to_csv(f'{data.filepath}\{future}.csv')
        print(f'[{future}] finished.')

        print(f'{count+100} of {len(data.futures)}\n')
    except Exception:
        pass

# get spread data
all_symbols = data.spots + data.futures
data.get_spread(all_symbols,timerspread=3600)

# It's more recommended to use the code below
'''
data.get_spread(data.spots,timerspread=3600)
data.get_spread(data.futures,timerspread=3600)
'''
