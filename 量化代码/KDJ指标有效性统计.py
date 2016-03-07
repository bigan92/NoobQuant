# -*- coding: utf-8 -*-
"""
Created on Wed Feb 03 13:26:53 2016

@author: Administrator
"""
#==============================================================================
# KDJ指标
#==============================================================================
import pandas as pd
import tushare as ts 
import matplotlib.pyplot as plt
import os
from conda.progressbar import *
import sys
import time
import gc
import re

def indicator_KDJ(stock_data):#KDJ指标计算函数
    # 计算KDJ指标
    low_list = pd.rolling_min(stock_data['low'], 9) #9天为一个周期，但前8个值为NaN
    low_list.fillna(value=pd.expanding_min(stock_data['low']), inplace=True) #将NaN用累积窗口计算的最小值代替
    high_list = pd.rolling_max(stock_data['high'], 9)
    high_list.fillna(value=pd.expanding_max(stock_data['high']), inplace=True)
    rsv = (stock_data['close'] - low_list) / (high_list - low_list) * 100
    stock_data['KDJ_K'] = pd.ewma(rsv, com=2, adjust=False)
    stock_data['KDJ_D'] = pd.ewma(stock_data['KDJ_K'], com=2, adjust=False)
    stock_data['KDJ_J'] = 3 * stock_data['KDJ_K'] - 2 * stock_data['KDJ_D']
    # 计算KDJ指标金叉、死叉情况
    stock_data['KDJ_金叉死叉'] = ''
    kdj_position = stock_data['KDJ_K'] > stock_data['KDJ_D']
    stock_data.loc[kdj_position[(kdj_position == True) & (kdj_position.shift() == False)].index, 'KDJ_金叉死叉'] = '金叉' #前一天K<D,当天K>D
    stock_data.loc[kdj_position[(kdj_position == False) & (kdj_position.shift() == True)].index, 'KDJ_金叉死叉'] = '死叉'
    # 通过复权价格计算接下来几个交易日的收益率
    for n in [1, 2, 3, 5, 10, 20]:
        stock_data['接下来'+str(n)+'个交易日涨跌幅'] = stock_data['close'].shift(-1*n) / stock_data['close'] - 1.0
    stock_data.dropna(how='any', inplace=True)# 删除所有有空值的数据行
    # 筛选出KDJ金叉的数据，并将这些数据合并到all_stock中
    stock_data = stock_data[(stock_data['KDJ_金叉死叉'] == '金叉')]
    if not stock_data.empty:
        return stock_data

r = re.compile('[#.]') #正则表达式
sdpath = os.getcwd()+'\股票数据\\'
sddir = os.listdir(sdpath)
lensd = len(sddir)
all_stock = pd.DataFrame()

startTime = time.time() #计时开始

pbar = ProgressBar().start() #进度条开始
i = 0;
for file in sddir:
    df_stock = pd.read_csv(sdpath+file, #路径
                      sep='\t', 
                      header = 1, #列名所在行
                      index_col = 0, #索引所在列
    #                      skiprows = 1, 
                      encoding = 'gbk') #包含中文，解码格式
    df_stock.dropna(how = 'any',inplace = 'True') #清除最后一行通达信
    if len(df_stock)<200:# 排除刚上市的股票
        continue
    df_stock.index = pd.to_datetime(df_stock.index)  #时间转换为与tushare对应的时间数据类型                   
    iterables = [r.split(file)[1], df_stock.index]# 股票代码，股票索引
    df_stock.index = pd.MultiIndex.from_product(iterables, names=['code', 'date']) # 生成多重索引
    
    df_stock.columns = ['open','high','low','close','volume','amount']
    all_stock = all_stock.append(indicator_KDJ(df_stock))
    
    pbar.update(int(i*100/(lensd-1)))
    i+= 1
pbar.finish() #进度条结束        
endTime = time.time() #计时结束
print('程序运行时间为%ds' %(endTime-startTime))

all_stock = all_stock[(all_stock!=float('inf'))&(all_stock!=float('-inf'))] #虽然是后复权数据，一些数据可能为负或0，造成计算收益率时可能除0，排除这些干扰项目
all_stock.dropna(how = 'any',inplace = 'True')
print()
print('历史上所有股票出现KDJ金叉的次数为%d，这些股票在：' %all_stock.shape[0])
print()
for n in [1, 2, 3, 5, 10, 20]:
    print ("金叉之后的%d个交易日内，" % n,)
    print ("平均涨幅为%.2f%%，" % (all_stock['接下来'+str(n)+'个交易日涨跌幅'].mean() * 100))
    print ("其中上涨股票的比例是%.2f%%。" % \
          (all_stock[all_stock['接下来'+str(n)+'个交易日涨跌幅'] > 0].shape[0]/float(all_stock.shape[0]) * 100) )

         

    