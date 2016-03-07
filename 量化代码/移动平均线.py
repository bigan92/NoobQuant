# -*- coding: utf-8 -*-
"""
Created on Mon Feb  8 14:24:58 2016

@author: Administrator
"""
#==============================================================================
# 移动平均线
#==============================================================================
import pandas as pd
import tushare as ts 

df = ts.get_hist_data('sh')
df.sort_index(inplace=True)

# 分别计算5日、20日、60日的移动平均线
ma_list = [5, 20, 60]
# 计算简单算术移动平均线MA - 注意：stock_data['close']为股票每天的收盘价
for ma in ma_list:
    df['MA_' + str(ma)] = pd.rolling_mean(df['close'], ma)
df.plot(y=['close','MA_5','MA_20','MA_60'])  
# 计算指数平滑移动平均线EMA    
for ma in ma_list:
    df['EMA_' + str(ma)] = pd.ewma(df['close'], span=ma)
df.plot(y=['close','EMA_5','EMA_20','EMA_60']) 