# coding: utf-8

# In[1]:


import pandas as pd
import ccxt
from datetime import datetime, timezone, timedelta
from datetime import date
import os
import sys
import time
import numpy
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import LSTM
from keras.layers import Dropout


# In[2]:


def print_chart(exchange, symbol, timeframe, from_datetime):
    #function to get candle chart for time period 
    #returns dataframe 
    
    #PARAMS
    #exchange - ccxt exchange object that determines which exchange to pull OHLCVS from
    #symbol - string that represent symbol from respective exchange
    #timeframe - string for intervals between each price
    #from_datetime - when to begin price /ticker information
    
    msec = 1000
    minute = 60 * msec
    hour = 60
    hold = 30


    from_timestamp = exchange.parse8601(from_datetime)

    now = exchange.milliseconds()

    data = []

    while from_timestamp < now:

        try:

            print(exchange.milliseconds(), 'Fetching candles starting from', exchange.iso8601(from_timestamp))
            ohlcvs = exchange.fetch_ohlcv(symbol, timeframe, from_timestamp)
            print(exchange.milliseconds(), 'Fetched', len(ohlcvs), 'candles')
            first = ohlcvs[0][0]
            last = ohlcvs[-1][0]
            print('First candle epoch', first, exchange.iso8601(first))
            print('Last candle epoch', last, exchange.iso8601(last))
            
            #either remove or include additoinal params like day or month , whatever ccxt allows
            from_timestamp += len(ohlcvs) * minute *hour
            data += ohlcvs

        except (ccxt.ExchangeError, ccxt.AuthenticationError, ccxt.ExchangeNotAvailable, ccxt.RequestTimeout) as error:

            print('Got an error', type(error).__name__, error.args, ', retrying in', hold, 'seconds...')
            time.sleep(hold)
    data = pd.DataFrame(data, columns=['Timestamp_ms','Open_Price', 'Highest_Price', 'Lowest_Price', 'Closing_Price','Volume'])
    
    return data

def label_perfect_trades( priceHistory):
    
    #labels perfect trades as peaks , valleys or neutral
    
    #params
    #priceHistory - dataframe of OHLCVS
    label_df = pd.DataFrame( columns=['Closing_Price', 'peak','valley','neutral'])
    label_df['Closing_Price'] = priceHistory['Closing_Price'].values
    triggerPrice = label_df['Closing_Price'].at[0]
    for i in range(len(label_df['Closing_Price'].values)-1):
        if  label_df['Closing_Price'].at[i+1] > triggerPrice +(triggerPrice *0.003):
            label_df['peak'].at[i+1] = 1
            triggerPrice = label_df['Closing_Price'].at[i+1]
        elif label_df['Closing_Price'].at[i+1] < triggerPrice -(triggerPrice *0.003):
            label_df['valley'].at[i+1] = 1
            triggerPrice =  label_df['Closing_Price'].at[i+1]
        else:
            label_df['neutral'].at[i+1] =1
            
    priceHistory = pd.concat([priceHistory, label_df.drop('Closing_Price',1)], 1)
            
    return priceHistory.fillna(0)

# In[3]:


symbol = 'BTC/USD'

from_datetime = '2017-09-01 00:00:00'

kraken = ccxt.kraken({
    'rateLimit': 3000,
    'enableRateLimit': True,
    # 'verbose': True,
                    })


btc_df =  print_chart(kraken, 'BTC/USD', '30m',from_datetime)


# In[4]:


btc_df.shape


# In[5]:


btc_timeSeries = label_perfect_trades(btc_df)


# In[9]:


btc_timeSeries.head()


# In[10]:


btc_train = btc_timeSeries[0:7444]
btc_test = btc_timeSeries[7445:9445]

train_targets = btc_train.drop(['Timestamp_ms', 'Highest_Price','Lowest_Price', 'Open_Price','Closing_Price','Volume'],1).values
test_targets = btc_test.drop(['Timestamp_ms', 'Highest_Price','Lowest_Price', 'Open_Price','Closing_Price','Volume'],1).values

btc_train = btc_train.values
btc_test = btc_test.values

btc_train = btc_train.reshape((btc_train.shape[0], 1, btc_train.shape[1]))
btc_test = btc_test.reshape((btc_test.shape[0], 1, btc_test.shape[1]))


# In[11]:


model = Sequential()
model.add(Dropout(0.2))
model.add(LSTM(3))
model.add(Dropout(0.2))
model.add(Dense(3, activation='softmax'))
model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['mae'])
model.fit(btc_train, train_targets, epochs=3, batch_size=1489, shuffle=False, validation_split=0.1)
# Final evaluation of the model
scores = model.evaluate(btc_test, test_targets, verbose=0)
print("Accuracy: %.2f%%" % (scores[1]*100))
