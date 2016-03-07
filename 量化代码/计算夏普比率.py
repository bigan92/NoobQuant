# -*- coding: utf-8 -*-
"""
Created on Sat Feb 20 21:25:00 2016

@author: Administrator
"""

#==============================================================================
# 计算夏普比率
#==============================================================================
import tushare as ts
import pandas as pd
import os
import math
sdpath = os.getcwd()+'\股票数据\\'
file = 'SH#600000.txt'
index_data = pd.read_csv(sdpath+file, #路径
                      sep='\t', 
                      header = 1, #列名所在行
                      index_col = 0, #索引所在列
    #                      skiprows = 1, 
                      encoding = 'gbk') #包含中文，解码格式
index_data.dropna(how = 'any',inplace = 'True') #清除最后一行通达信
index_data.index = pd.to_datetime(index_data.index)
index_data = index_data['2010':] # 选择时间范围
index_data.index.name = 'date'
index_data.columns = ['open','high','low','close','volume','amount']

dailyRet = (index_data['close']-index_data['close'].shift(1)) / index_data['close'].shift(1)
excessRet = dailyRet - 0.025/252
sharpeRatio = math.pow(252,0.5)*excessRet.mean()/excessRet.std()