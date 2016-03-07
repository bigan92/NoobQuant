# -*- coding: utf-8 -*-
"""
Created on Mon Feb  8 14:27:36 2016

@author: Administrator
"""
#==============================================================================
# 创业板平均市盈率 
#==============================================================================
#import pandas as pd
import tushare as ts 


df = ts.get_stock_basics()
cyb = df.ix[[code for code in df.index if code[0]=='3']] # 3为创业板开头数字
market_value = cyb['esp']*cyb['pe']*cyb['totals']
net_profits = cyb['esp']*cyb['totals']
cyb_ape = market_value.sum()/net_profits.sum()# 创业板平均市盈率
print()
print('平均市盈率为%d' %cyb_ape)