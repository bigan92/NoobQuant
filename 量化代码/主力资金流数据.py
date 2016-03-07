# -*- coding: utf-8 -*-
"""
Created on Tue Feb  9 18:02:42 2016

@author: Administrator
"""
#==============================================================================
# 主力资金流数据
#==============================================================================
import tushare as ts
stock_data = ts.get_tick_data('600428',date='2016-02-05')
# 计算平均每笔成交量
print('平均每笔成交量:%d手' % stock_data['volume'].mean())
# 计算资金流入流出
data = stock_data.groupby('type')['amount'].sum()
if '买盘' in data.index:
    print('资金流入:%d元' % data['买盘'])
if '卖盘' in data.index:
    print('资金流出:%d元' % data['卖盘'])
# 计算主力资金流入流出
data = stock_data[stock_data['volume']>500].groupby('type')['amount'].sum()
if '买盘' in data.index:
    print('主力资金流入:%d元' % data['买盘'])
if '卖盘' in data.index:
    print('主力资金流出:%d元' % data['卖盘'])