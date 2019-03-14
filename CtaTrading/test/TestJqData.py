# encoding: UTF-8
import jqdatasdk
import time
import talib
import numpy as np

# jqdatasdk.auth('13268108673', 'king20110713')
jqdatasdk.auth('13824472562', '472562')
security = 'JM8888.XDCE'
pricePosi_top = 0
pricePosi_bot = 4
start_date = '2018-10-19 00:00:00'#time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time() - 2592000 * 12))
end_date = '2018-10-26 00:00:00'#time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
df = jqdatasdk.get_price(security=security, start_date=start_date, end_date=end_date, frequency='5m', fields=['close'])
close = [float(x) for x in df['close']]
df['EMA5'] = talib.EMA(np.array(close), timeperiod=5)
df['EMA10'] = talib.EMA(np.array(close), timeperiod=10)
df['EMA20'] = talib.EMA(np.array(close), timeperiod=20)
df['EMA40'] = talib.EMA(np.array(close), timeperiod=40)
df['EMA60'] = talib.EMA(np.array(close), timeperiod=60)
indexList = df[df.EMA60 == df.EMA60].index.tolist()

pricePositions = []
isHoldingShort = False
isHoldingBuy = False
isHolding = False
shortStartDate = None
shortEndDate = None
buyStartDate = None
buyEndDate = None
shortStartClose = 0
shortEndClose = 0
buyStartClose = 0
buyEndClose = 0
fetchPoint = 0
fetchRate = 1
lockClose = 0
rates = []

for index in indexList:

    #准备阶段：准备好（1）5日均线位置（2）当前价格-------------------------------------------------------------------------------------------------
    ema5 = df.loc[index, 'EMA5']
    emas = sorted([ema5, df.loc[index, 'EMA10'], df.loc[index, 'EMA20'], df.loc[index, 'EMA40'], df.loc[index, 'EMA60']], reverse=True)
    pricePosi = 0
    for ema in emas:
        if ema == ema5:
            break # 找到5日线所在位置 0：所有均线最上方（第一次循环就break） emas-1: 所有均线最下方（最后break）
        pricePosi = pricePosi + 1

    price = df.loc[index, 'close']
    #准备完成----------------------------------------------------------------------------------------------------------------------------------

    # 如果在holding，持仓中。只会触发平仓和锁仓，不会去开仓。
    if isHolding == True:
        # 持有多仓
        if isHoldingBuy == True:
            if lockClose == 0:
                if price < buyStartClose:# 持有多仓 -> 当前价格小于开仓价，开始亏损
                    lockClose = price    # 执行锁仓
            else:
                if price> buyStartClose:# 持有多仓 -> 当前价格大于开仓价锁仓 -> 停止亏损
                    lockClose = 0        # 取消锁仓

            if pricePosi > pricePosi_top:
                buyEndClose = price
                if lockClose != 0:
                    buyEndClose = lockClose
                    lockClose = 0
                isHolding = False
                isHoldingBuy = False
                fetchPoint = fetchPoint + (buyEndClose - buyStartClose)
                fetchRate = fetchRate * (1+((buyEndClose - buyStartClose) / buyStartClose))
                buyEndDate = index
                rate = round(((buyEndClose - buyStartClose) / buyStartClose), 4) * 100
                rates.append(rate)
                print("B " + str(buyStartDate) + "---" + str(buyEndDate) + ": " +
                      str(rate) + "--->" + str(buyEndClose - buyStartClose))
                buyStartDate = None
                buyEndDate = None
                buyEndClose = 0
                buyStartClose = 0
        elif isHoldingShort == True:

            if lockClose == 0:
                if price > shortStartClose:# 持有空仓 -> 当前价格大于开仓价，开始亏损
                    lockClose = price      # 一半仓位反手开多，执行锁仓
            else:
                if shortStartClose > price:# 持有空仓 -> 当前价格小于开仓价，停止亏损
                    lockClose = 0          # 开多的一半仓位反手开空，停止锁仓

            if pricePosi < pricePosi_bot:
                shortEndClose = price
                if lockClose != 0:
                    shortEndClose = lockClose
                    lockClose = 0
                isHolding = False
                isHoldingShort = False
                fetchPoint = fetchPoint + (shortStartClose - shortEndClose)
                fetchRate = fetchRate * (1+((shortStartClose - shortEndClose) / shortStartClose))
                shortEndDate = index
                rate = round((shortStartClose - shortEndClose) / shortStartClose, 4) * 100
                rates.append(rate)
                print("S " + str(shortStartDate) + "---" + str(shortEndDate) + ": "
                      + str(rate) + "--->" + str(shortStartClose - shortEndClose))
                shortStartDate = None
                shortEndDate = None
                shortStartClose = 0
                shortEndClose = 0

        # holding状态，不进入开仓环节，直接continue
        continue

    # 如果持币，则只会进入开仓判断
    if pricePosi == 0:
        isHolding = True
        isHoldingBuy = True
        buyStartDate = index
        buyStartClose = price
    if pricePosi == 4:
        isHolding = True
        isHoldingShort = True
        shortStartDate = index
        shortStartClose = price

rates = sorted(rates, reverse=True)
totalR = 1
for rate in rates:
    totalR = totalR * (1 + (rate/100))
print(fetchPoint)
print(fetchRate)
print(rates)
print(totalR)
