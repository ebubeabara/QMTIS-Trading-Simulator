#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 14 01:20:18 2017

@author: jamesli
"""

import requests
import datetime
import pandas as pd

def geturl():

    ticker = str(input("Enter ticker symbol: "))
    ticker_api = "https://query1.finance.yahoo.com/v8/finance/chart/" + ticker + "?range=1d&includePrePost=false&interval=1m&corsDomain=finance.yahoo.com&.tsrc=finance&output=json"
    return (json_data(ticker_api, ticker))

def json_data(ticker_api, ticker):

    ticker_api = requests.get(ticker_api).json()
    try:
        get_info = get_close_price(ticker_api)
        print("Last close price (" + ticker + "): " + "%.2f" % get_info['close_price'] + "\n" + get_info['time'])
        get_plot(ticker_api)
        
    except TypeError:
        print("Please enter a valid ticker symbol.")
        geturl()
        
def get_close_price(ticker_api):
    i = -1
    error_count = 0
    if (ticker_api['chart']['result'][0]['indicators']['quote'][0]['close'][-1] is not None):
        close_price = ticker_api['chart']['result'][0]['indicators']['quote'][0]['close'][-1]
        close_time = datetime.datetime.fromtimestamp(ticker_api['chart']['result'][0]['timestamp'][-1])
        time_fmt = "%d-%m-%y %H:%M:%S"
        return {'close_price':close_price, 'time':close_time.strftime(time_fmt)}
    else:
        while (ticker_api['chart']['result'][0]['indicators']['quote'][0]['close'][i] is None):
            i -= 1
            close_price = ticker_api['chart']['result'][0]['indicators']['quote'][0]['close'][i]
            close_time = datetime.datetime.fromtimestamp(ticker_api['chart']['result'][0]['timestamp'][i])
            time_fmt = "%d-%m-%y %H:%M:%S"
            error_count += 1
            if error_count>60: #60 because assumes that there won't be empty price for more than 60mins
                raise Exception('API error! contact Admin')
        return {'close_price':close_price, 'time':close_time.strftime(time_fmt)}

def get_plot(ticker_api):
    
    time_array = []
    
    for timestamp in ticker_api['chart']['result'][0]['timestamp']:
        epochToDateTime = datetime.datetime.fromtimestamp(timestamp)
        time_array.append(epochToDateTime)
    
    close_price = ticker_api['chart']['result'][0]['indicators']['quote'][0]['close']
    
    for i in range(len(close_price)): #replace None with previous recorded value to avoid gaps in graph
        if close_price[i] is None:
            temp = i-1
            close_price[i] = close_price[temp]
            #note: if first element is None, it will not print the first element
    
    data = {'time':time_array, 'price':close_price}
    
    df = pd.DataFrame(data, columns = ['time','price'])

    df['time'] = pd.to_datetime(df['time']) #parse datetime to pandas readable time
    df.index = df['time']
    del df['time']
    
    return df.plot()

geturl()

# server needs to direct to error page if API error! is raised
# there will be a few minutes of api down time when market opens
# need to include date in the graph
# need to allow users to choose different graph intervals
# need to include ticker symbol on graph
# need to separate ticker and functions interlinks for actual implementation