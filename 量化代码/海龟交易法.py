# -*- coding: utf-8 -*-
"""
Created on Mon Feb  8 14:33:26 2016

@author: Administrator
"""

#==============================================================================
# 海龟交易法
#==============================================================================
import tushare as ts
import pandas as pd
import os
sdpath = os.getcwd()+'\股指数据\\'
file = 'SH#999999.txt'
index_data = pd.read_csv(sdpath+file, #路径
                      sep='\t', 
                      header = 1, #列名所在行
                      index_col = 0, #索引所在列
    #                      skiprows = 1, 
                      encoding = 'gbk') #包含中文，解码格式
index_data.dropna(how = 'any',inplace = 'True') #清除最后一行通达信
index_data.index = pd.to_datetime(index_data.index)
index_data = index_data['2012':] # 选择时间范围
index_data.index.name = 'date'
index_data.columns = ['open','high','low','close','volume','amount']

# ==========计算海龟交易法则的买卖点
# 设定海龟交易法则的两个参数，当收盘价大于最近N1天的最高价时买入，当收盘价低于最近N2天的最低价时卖出
# 这两个参数可以自行调整大小，但是一般N1 > N2
N1 = 20
N2 = 10
# 通过rolling_max方法计算最近N1个交易日的最高价
index_data['最近N1个交易日的最高点'] =  pd.rolling_max(index_data['high'], N1)
# 对于上市不足N1天的数据，取上市至今的最高价
index_data['最近N1个交易日的最高点'].fillna(value=pd.expanding_max(index_data['high']), inplace=True)

# 通过相似的方法计算最近N2个交易日的最低价
index_data['最近N2个交易日的最低点'] =  pd.rolling_min(index_data['low'], N2)
index_data['最近N2个交易日的最低点'].fillna(value=pd.expanding_min(index_data['low']), inplace=True)

# 当当天的【close】> 昨天的【最近N1个交易日的最高点】时，将【收盘发出的信号】设定为1
buy_index = index_data[index_data['close'] > index_data['最近N1个交易日的最高点'].shift(1)].index
index_data.loc[buy_index, '收盘发出的信号'] = 1
# 当当天的【close】< 昨天的【最近N2个交易日的最低点】时，将【收盘发出的信号】设定为0
sell_index = index_data[index_data['close'] < index_data['最近N2个交易日的最低点'].shift(1)].index
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


# 输出数据到指定文件
index_data[['high', 'low', 'close', '最近N1个交易日的最高点',
            '最近N2个交易日的最低点', '当天的仓位', '资金指数']].to_csv('turtle.csv', index=False, encoding='gbk')
            
# 计算每年指数的收益以及海龟交易法则的收益
index_data['海龟法则每日涨跌幅'] = price_change * index_data['当天的仓位']
year_rtn = index_data['海龟法则每日涨跌幅'].\
               resample('A', how=lambda x: (x+1.0).prod() - 1.0) * 100
print('海龟法则年收益率:')               
print(year_rtn)
print()

# 计算年化收益率
total_days = (index_data.index[-1]-index_data.index[0]).days
avg_year_rtn = (index_data['资金涨幅'][-1]**(365/total_days)-1)*100
print('海龟法则年平均收益率:%.2f%%' % avg_year_rtn)
print()

# 计算最大回撤
max_drawdown = (1- index_data['资金指数']/pd.expanding_max(index_data['资金指数'])).max()*100
print('最大回撤:%.2f%%' % max_drawdown)

# 计算最长亏损时间
max_drawdownDuration = index_data['资金指数'].cummax().value_counts().iloc[0]
print('最长亏损时间:%d天' % max_drawdownDuration)

# 绘图
index_data[['close','资金指数']].plot()


