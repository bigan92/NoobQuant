# -*- coding: utf-8 -*-
"""
Created on Sat Feb 27 09:49:41 2016

@author: Administrator
"""

#==============================================================================
# MACD指标
#==============================================================================
import tushare as ts
import pandas as pd
import os
import talib
sdpath = os.getcwd()+'\股票数据\\'
file = 'SH#600196.txt'
index_data = pd.read_csv(sdpath+file, #路径
                      sep='\t', 
                      header = 1, #列名所在行
                      index_col = 0, #索引所在列
    #                      skiprows = 1, 
                      encoding = 'gbk') #包含中文，解码格式
index_data.dropna(how = 'any',inplace = 'True') #清除最后一行通达信
index_data.index = pd.to_datetime(index_data.index)
index_data = index_data['1992':] # 选择时间范围
index_data.index.name = 'date'
index_data.columns = ['open','high','low','close','volume','amount']
# 调用TA_lib库函数
macd, signal, hist = talib.MACD(index_data['close'].values, fastperiod=12, slowperiod=26, signalperiod=9)
# 记录尾盘发出的买入，卖出的信号点，
position = pd.Series(hist>0,index=index_data.index)
buy_index = position[(position == True)&(position.shift() == False)].index
index_data.loc[buy_index, '收盘发出的信号'] = 1
sell_index = position[(position == False)&(position.shift() == True)].index
index_data.loc[sell_index, '收盘发出的信号'] = 0
 
# 计算每天的仓位，当天持有上证指数时，仓位为1，当天不持有上证指数时，仓位为0
index_data['当天的仓位'] = index_data['收盘发出的信号'].shift(1)#头一天发出信号后尾盘买入，今天享受全部涨幅
index_data['当天的仓位'].fillna(method='ffill', inplace=True)

# 计算每天的涨幅，
price_change = (index_data['close']-index_data['close'].shift(1)) / index_data['close'].shift(1) #当日比前一日的涨跌幅度
# 考虑到手续费，修正每天涨幅：买：0.06%+0.025% 卖：0.1%+0.06%+0.025%
trade_time = index_data['当天的仓位'].shift(-1)-index_data['当天的仓位'] #寻找交易发生的时间:1为买入时间，-1为卖出时间
price_change[trade_time == 1]= (price_change[trade_time == 1]+1)*(1-0.00085)-1 #买的时间,注意先加1计算费率，扣除费率后减1
price_change[trade_time == -1]= (price_change[trade_time == -1]+1)*(1-0.00185)-1 #卖的时间
index_data['资金涨幅'] = (price_change * index_data['当天的仓位'] + 1.0).cumprod()
index_data['资金指数'] = index_data['资金涨幅'] * index_data.iloc[0]['close']

# 计算每年指数的收益以及MACD策略的收益
index_data['MACD策略每日涨跌幅'] = price_change * index_data['当天的仓位']
year_rtn = index_data['MACD策略每日涨跌幅'].\
               resample('A', how=lambda x: (x+1.0).prod() - 1.0) * 100
print('MACD策略年收益率:')               
print(year_rtn)
print()

# 计算年化收益率
total_days = (index_data.index[-1]-index_data.index[0]).days
avg_year_rtn = (index_data['资金涨幅'][-1]**(365/total_days)-1)*100
print('MACD策略年平均收益率:%.2f%%' % avg_year_rtn)
print()

# 计算最大回撤
max_drawdown = (1- index_data['资金指数']/pd.expanding_max(index_data['资金指数'])).max()*100
print('最大回撤:%.2f%%' % max_drawdown)

# 计算最长亏损时间
max_drawdownDuration = index_data['资金指数'].cummax().value_counts().iloc[0]
print('最长亏损时间:%d天' % max_drawdownDuration)

# 绘图
index_data[['close','资金指数']].plot()
