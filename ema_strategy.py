from vnpy.app.cta_strategy import (
    CtaTemplate,
    StopOrder,
    TickData,
    BarData,
    TradeData,
    OrderData,
    BarGenerator,
    ArrayManager,
)
import talib
import jqdatasdk
import numpy as np
import PyBase.Util as util

def getAdvancedData(df, security, frequency, nowTimeString):
    newRow = None
    newIndex = None
    jqdatasdk.auth('13268108673', 'king20110713')
    if df is None:
        df = jqdatasdk.get_price(
            security=security,
            count=500,
            end_date=nowTimeString[0:nowTimeString.rindex(':') + 1] + '30',
            frequency=frequency,
            fields=['close', 'open', 'volume', 'high', 'low', 'money']
        )
    else:
        newDf = jqdatasdk.get_price(
            security=security,
            count=1,
            end_date=nowTimeString[0:nowTimeString.rindex(':') + 1] + '30',
            frequency=frequency,
            fields=['close', 'open', 'volume', 'high', 'low', 'money']
        )
        newIndex = newDf.index.tolist()[0]
        newRow = newDf.loc[newIndex]
    if newRow is not None:
        df.loc[newIndex] = newRow
    close = [float(x) for x in df['close']]
    high = [float(x) for x in df['high']]
    low = [float(x) for x in df['low']]
    df['EMA5'] = talib.EMA(np.array(close), timeperiod=5)
    df['EMA10'] = talib.EMA(np.array(close), timeperiod=10)
    df['EMA20'] = talib.EMA(np.array(close), timeperiod=20)
    df['EMA40'] = talib.EMA(np.array(close), timeperiod=40)
    df['EMA60'] = talib.EMA(np.array(close), timeperiod=60)
    df['EMA7'] = talib.EMA(np.array(close), timeperiod=7)
    df['EMA23'] = talib.EMA(np.array(close), timeperiod=23)
    df['ADX'] = talib.ADX(np.array(high), np.array(low), np.array(close), timeperiod=6)
    df.drop([df.index.tolist()[0]], inplace=True)
    return df

def getPricePosiArray(df):
    indexList = df[df.EMA60 == df.EMA60].index.tolist()
    pricePositions = []
    for index in indexList:
        ema7 = df.loc[index, 'EMA7']
        emas = sorted(
            # [ema5, df.loc[index, 'EMA10'], df.loc[index, 'EMA20'], df.loc[index, 'EMA40'], df.loc[index, 'EMA60']],
            [ema7, df.loc[index, 'EMA23']],
            reverse=True)
        pricePosi = 0
        for ema in emas:
            if ema == ema7:
                break
            pricePosi = pricePosi + 1
        pricePositions.append(pricePosi)
    return pricePositions

def getVolumeArrows(df):
    indexList = df[df.EMA60 == df.EMA60].index.tolist()
    i = 0
    arr = []
    for index in indexList:
        count = _getVolumeArrow(df, indexList, i)
        arr.append(count)
        i = i + 1
    return arr

def _getVolumeArrow(df, indexList, indexCount):
    if indexCount is not None:
        indexList = indexList[0:indexCount + 1]
    volumes = []
    for index in indexList:
        v = df.loc[index, 'volume']
        volumes.append(v)
    count = 0
    max = None
    while count < indexList.__len__() - 1:
        v = volumes[indexList.__len__() - count - 1]
        if max is None:
            max = v
        elif v * 1.2 > max:
            return count - 1
        count = count + 1
    return count

def getOpen2CloseRates(df):
    opens = [float(x) for x in df['open']]
    closes = [float(x) for x in df['close']]
    arr = []
    i = 0
    for open in opens:
        close = closes[i]
        rate = util.getRate(open, close)
        i = i + 1
        arr.append(rate)
    return arr

def getAvgOpen2CloseRates(df):
    rates = getOpen2CloseRates(df)
    i = 0
    arr = []
    while i < rates.__len__():
        arr.append(round(np.mean(rates[0:i+1]), 4))
        i = i + 1
    return arr

def getSameStateTimes():
    pricePositions = getPricePosiArray(df)
    i = 0
    count = 0
    pre = None
    while i < pricePositions.__len__():
        pp = pricePositions[i]
        if pre is None or pre == pp:
            count = count + 1
        else:
            count = 0
        i = i + 1

def getNearMaxClosePrice(df=None):
    pricePositions = getPricePosiArray(df)
    indexList = df[df.EMA60 == df.EMA60].index.tolist()
    closes = []
    for index in indexList:
        closes.append(df.loc[index, 'close'])
    i = pricePositions.__len__() - 1
    nowPricePosition = pricePositions[-1]
    while (i - 1) > 0:
        pp = pricePositions[i - 1]
        if pp == nowPricePosition:
            i = i - 1
        else:
            break
    closes = closes[i:]
    if nowPricePosition == 0:
        maxClose = max(closes)
        return maxClose
    return None


def getNearMinClosePrice(df=None):
    pricePositions = getPricePosiArray(df)
    indexList = df[df.EMA60 == df.EMA60].index.tolist()
    closes = []
    for index in indexList:
        closes.append(df.loc[index, 'close'])
    i = pricePositions.__len__() - 1
    nowPricePosition = pricePositions[-1]
    while (i - 1) > 0:
        pp = pricePositions[i - 1]
        if pp == nowPricePosition:
            i = i - 1
        else:
            break
    closes = closes[i:]
    if nowPricePosition == 0:
        pass
    else:
        return min(closes)
    return None

def getNowEarningRate(df):
    pricePositions = getPricePosiArray(df)
    indexList = df[df.EMA60 == df.EMA60].index.tolist()
    closes = []
    for index in indexList:
        closes.append(df.loc[index, 'close'])
    i = pricePositions.__len__() - 1
    nowPricePosition = pricePositions[-1]
    while (i - 1) > 0:
        pp = pricePositions[i - 1]
        if pp == nowPricePosition:
            i = i - 1
        else:
            break
    closes = closes[i:]
    isDouing = getNearMaxClosePrice(df) is not None
    startPrice = closes[0]
    nowPrice = closes[-1]
    if isDouing is True:
        return util.getRate(startPrice, nowPrice)
    else:
        return util.getRate(nowPrice, startPrice)

def getDangerRate(df):
    indexList = df[df.EMA60 == df.EMA60].index.tolist()
    nowPrice = df.loc[indexList[-1], 'close']
    maxClosePrice = getNearMaxClosePrice(df)
    minClosePrice = getNearMinClosePrice(df)
    if maxClosePrice is not None:
        rate = util.getRate(fromPrice=maxClosePrice, toPrice=nowPrice)
    else:
        rate = util.getRate(fromPrice=minClosePrice, toPrice=nowPrice)
    return rate

def pushPosition(position):
    o = {'available': True, 'position': position, 'createtime': util.getYMDHMS()}
    position_flow = util.getProperty('position_flow')
    if position_flow is None:
        util.setProperty('position_flow', [o])
    else:
        position_flow.append(o)
        util.removeProperty('position_flow')
        util.setProperty('position_flow', position_flow)

def getNowPosition():
    position_flow = util.getProperty('position_flow')
    if position_flow is None:
        return 0
    else:
        return int(position_flow[-1].get('position'))

def isChangeTo(df):
    nowPricePosi = getPricePosiArray(df)[-1]
    prePricePosi = getPricePosiArray(df)[-2]
    if nowPricePosi != prePricePosi and nowPricePosi == 0:
        return "UP"
    elif nowPricePosi != prePricePosi and nowPricePosi == 1:
        return "DOWN"
    else:
        return "STILL"

def isChangeToDOWN(df):
    nowPricePosi = getPricePosiArray(df)[-1]
    prePricePosi = getPricePosiArray(df)[-2]
    if nowPricePosi != prePricePosi and nowPricePosi == 1:
        return True
    else:
        return False

def changeFromNowCount(df):
    pricePositions = getPricePosiArray(df)
    pricePositions = pricePositions[-200:]
    pre = None
    i = pricePositions.__len__() - 1
    count = 0
    while i > 0:
        pricePosition = pricePositions[i]
        if pre is None:
            pre = pricePosition
        elif pre is not None:
            if pre != pricePosition:
                break
        count = count + 1
        i = i - 1
    return count

def loop(df=None, security='RB9999.XSGE', frequency='15m', nowTimeString=util.getYMDHMS()):
    df = getAdvancedData(df, security=security, frequency=frequency, nowTimeString=nowTimeString)
    status = isChangeTo(df)
    ADXs = [float(x) for x in df[df.ADX == df.ADX]['ADX']]
    cfn_count = changeFromNowCount(df)
    if status == 'STILL':
        dangerRate = getDangerRate(df) # dangerRate的容忍度应该由earningRate决定，两个是正相关。能容忍利润做筹码，厌恶本金损失
        earningRate = getNowEarningRate(df)
        if dangerRate < -0.5 or earningRate < -0.5:
            pushPosition(0)
    elif status == 'DOWN':
        pushPosition(1)
    else:
        pushPosition(-1)

df = None
loop(df=df, security='TA8888.XZCE')


    # er = getNowEarningRate(df)
    # eRate = getNowEarningRate(df)
    # print(er)
    # pricePositions = getPricePosiArray(df)
    # maxClosePrice = getNearMaxClosePrice(df)
    # minClosePrice = getNearMinClosePrice(df)
    # if maxClosePrice is not None:
    #     print('maxClosePrice: ' + str(maxClosePrice))
    # else:
    #     print('minClosePrice: ' + str(minClosePrice))

    # volumeArrows = getVolumeArrows(df)
    # rates = getOpen2CloseRates(df)
    # avgrates = getAvgOpen2CloseRates(df)
    # i = 0
    # indexList = df[df.EMA60 == df.EMA60].index.tolist()
    # for pricePosition in pricePositions:
    #     print(str(indexList[i]) + ': pp:' + str(pricePosition) + " -> vr:" + str(volumeArrows[i]) + " -> rate:" + str(rates[i]) + " -> avgrate:" + str(avgrates[i]))
    #     i = i + 1

# df = None
# state = {'kon': 0, 'duo': 0}
# timeArr = util.getTimeSerial(starttime='2019-03-02 09:00:00', count=100000, periodSec=30)
# for nowTimeString in timeArr:
#     loop(df=df, state=state, security='RB9999.XSGE', frequency='10m', nowTimeString=nowTimeString)
#     continue
#
# print(timeArr)





#
# class DoubleMaStrategy(CtaTemplate):
#     author = '武磊'
#
#     fast_window = 10
#     slow_window = 20
#
#     fast_ma0 = 0.0
#     fast_ma1 = 0.0
#
#     slow_ma0 = 0.0
#     slow_ma1 = 0.0
#
#     parameters = ['fast_window', 'slow_window']
#     variables = ['fast_ma0', 'fast_ma1', 'slow_ma0', 'slow_ma1']
#
#     def __init__(self, cta_engine, strategy_name, vt_symbol, setting):
#         """"""
#         super(DoubleMaStrategy, self).__init__(
#             cta_engine, strategy_name, vt_symbol, setting
#         )
#
#         self.bg = BarGenerator(self.on_bar)
#         self.am = ArrayManager()
#
#     def on_init(self):
#         """
#         Callback when strategy is inited.
#         """
#         self.write_log("策略初始化")
#         self.load_bar(10)
#
#     def on_start(self):
#         """
#         Callback when strategy is started.
#         """
#         self.write_log("策略启动")
#         self.put_event()
#
#     def on_stop(self):
#         """
#         Callback when strategy is stopped.
#         """
#         self.write_log("策略停止")
#
#         self.put_event()
#
#     def on_tick(self, tick: TickData):
#         """
#         Callback of new tick data update.
#         """
#         self.bg.update_tick(tick)
#
#     def on_bar(self, bar: BarData):
#         """
#         Callback of new bar data update.
#         """
#
#         am = self.am
#         am.update_bar(bar)
#         if not am.inited:
#             return
#
#         fast_ma = am.sma(self.fast_window, array=True)
#         self.fast_ma0 = fast_ma[-1]
#         self.fast_ma1 = fast_ma[-2]
#
#         slow_ma = am.sma(self.slow_window, array=True)
#         self.slow_ma0 = slow_ma[-1]
#         self.slow_ma1 = slow_ma[-2]
#
#         cross_over = self.fast_ma0 > self.slow_ma0 and self.fast_ma1 < self.slow_ma1
#         cross_below = self.fast_ma0 < self.slow_ma0 and self.fast_ma1 > self.slow_ma1
#
#         if cross_over:
#             if self.pos == 0:
#                 self.buy(bar.close_price, 1)
#             elif self.pos < 0:
#                 self.cover(bar.close_price, 1)
#                 self.buy(bar.close_price, 1)
#
#         elif cross_below:
#             if self.pos == 0:
#                 self.short(bar.close_price, 1)
#             elif self.pos > 0:
#                 self.sell(bar.close_price, 1)
#                 self.short(bar.close_price, 1)
#
#         self.put_event()
#
#     def on_order(self, order: OrderData):
#         """
#         Callback of new order data update.
#         """
#         pass
#
#     def on_trade(self, trade: TradeData):
#         """
#         Callback of new trade data update.
#         """
#         self.put_event()
#
#     def on_stop_order(self, stop_order: StopOrder):
#         """
#         Callback of stop order update.
#         """
#         pass
