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
import time
from functools import reduce

cond_er = 0.8
cond_before_er = 0.8
cond_after_er = 1.2
adx_timeperiod = 4
adx_edge = 30
fast_ema = 6
slow_ema = 11
timeArr = util.getTimeSerial(starttime='2018-10-29 09:20:00', count=2000000, periodSec=61)
df = None
security = 'PP8888.XDCE'
frequency = '30m'
msg = {
    'df': df,
    'position': 0,
    'force_waiting_count': 0,
    'open': 0,
    'clearRates': [],
    'tmp_rates_every_step': [],
    'open_after_next_change': False
}
def getAdvancedData(df, security, frequency, nowTimeString):
    newRow = None
    newIndex = None
    # jqdatasdk.auth('13268108673', 'king20110713')
    jqdatasdk.auth('13824472562', '472562')
    if df is None:
        df = jqdatasdk.get_price(
            security=security,
            count=500,
            end_date=nowTimeString[0:nowTimeString.rindex(':') + 1] + '30',
            frequency=frequency,
            fields=['close', 'open', 'volume', 'high', 'low']
        )
    else:
        newDf = jqdatasdk.get_price(
            security=security,
            count=1,
            end_date=nowTimeString[0:nowTimeString.rindex(':') + 1] + '30',
            frequency=frequency,
            fields=['close', 'open', 'volume', 'high', 'low']
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
    df['EMAF'] = talib.EMA(np.array(close), timeperiod=fast_ema)
    df['EMAS'] = talib.EMA(np.array(close), timeperiod=slow_ema)
    df['ADX'] = talib.ADX(np.array(high), np.array(low), np.array(close), timeperiod=adx_timeperiod)
    # df['ADX'] = util.adx(highs=np.array(high), lows=np.array(low), closes=np.array(close))
    df.drop([df.index.tolist()[0]], inplace=True)
    # print('---->get_query_count(): ' + str(jqdatasdk.get_query_count()))
    return df


def getPricePosiArray(df):
    indexList = df[df.EMA60 == df.EMA60].index.tolist()
    pricePositions = []
    for index in indexList:
        emafast = df.loc[index, 'EMAF']
        emas = sorted(
            # [ema5, df.loc[index, 'EMA10'], df.loc[index, 'EMA20'], df.loc[index, 'EMA40'], df.loc[index, 'EMA60']],
            [emafast, df.loc[index, 'EMAS']],
            reverse=True)
        pricePosi = 0
        for ema in emas:
            if ema == emafast:
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


def getNearMaxClosePrice(df=None, preCount=0):
    pricePositions = getPricePosiArray(df)
    indexList = df[df.EMA60 == df.EMA60].index.tolist()
    if preCount > 0:
        pricePositions = pricePositions[0:-preCount - 1]
        indexList = indexList[0:-preCount - 1]
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


def getNearMinClosePrice(df=None, preCount=0):
    pricePositions = getPricePosiArray(df)
    indexList = df[df.EMA60 == df.EMA60].index.tolist()
    if preCount > 0:
        pricePositions = pricePositions[0:-preCount - 1]
        indexList = indexList[0:-preCount - 1]
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


def getNowEarningRate(df, preCount=0):
    pricePositions = getPricePosiArray(df)
    indexList = df[df.EMA60 == df.EMA60].index.tolist()
    if preCount > 0:
        pricePositions = pricePositions[0:-preCount - 1]
        indexList = indexList[0:-preCount - 1]
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


def getDangerRate(df, preCount=0):
    indexList = df[df.EMA60 == df.EMA60].index.tolist()
    if preCount > 0:
        indexList = indexList[0:-preCount - 1]
    nowPrice = df.loc[indexList[-1], 'close']
    maxClosePrice = getNearMaxClosePrice(df, preCount)
    minClosePrice = getNearMinClosePrice(df, preCount)
    if maxClosePrice is not None:
        rate = util.getRate(fromPrice=maxClosePrice, toPrice=nowPrice)
    else:
        rate = util.getRate(fromPrice=nowPrice, toPrice=minClosePrice)
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
    pps = getPricePosiArray(df)
    nowPricePosi = pps[-1]
    prePricePosi = pps[-2]
    if nowPricePosi != prePricePosi and nowPricePosi == 0:
        return "UP"
    elif nowPricePosi != prePricePosi and nowPricePosi == 1:
        return "DOWN"
    else:
        return "STILL"


def isChangeToDOWN(df):
    pps = getPricePosiArray(df)
    nowPricePosi = pps[-1]
    prePricePosi = pps[-2]
    if nowPricePosi != prePricePosi and nowPricePosi == 1:
        return True
    else:
        return False


def changeFromNowCount(df):
    pps = getPricePosiArray(df)
    pricePositions = pps[-200:]
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


def get_bar_rates(df=None, len=20):
    bar_rates = []
    closes = [float(x) for x in df['close']]
    opens = [float(x) for x in df['open']]
    i = 0
    while i < len:
        rate = util.getRate(fromPrice=opens[-i - 1], toPrice=closes[-i - 1])
        bar_rates.append(rate)
        i = i + 1
    return bar_rates


def getATR(df=None, len=20):
    arr = get_bar_rates(df=df, len=len)
    return np.mean(arr)

def removeTreses():
    util.removeProperty('tmp_treses')

def appendTreses(tmp_rates_every_step):
    tmp_treses = util.getProperty('tmp_treses')
    if tmp_treses is not None:
        tmp_treses.append(tmp_rates_every_step)
    else:
        tmp_treses = [tmp_rates_every_step]
    util.setProperty('tmp_treses', tmp_treses)

def loop(security=None, frequency=None, nowTimeString=None, msg=None):
    df = msg.get('df')
    position = msg.get('position')
    force_waiting_count = msg.get('force_waiting_count')
    open = msg.get('open')
    clearRates = msg.get('clearRates')
    tmp_rates_every_step = msg.get('tmp_rates_every_step')
    open_after_next_change = msg.get('open_after_next_change')
    df = getAdvancedData(df, security=security, frequency=frequency, nowTimeString=nowTimeString)
    # atr = getATR(df=df, len=20)
    closes = [float(x) for x in df['close']]
    if force_waiting_count > 0:
        force_waiting_count = force_waiting_count - 1
        print(nowTimeString + ": ForceWaiting...")
        return {
            'df': df,
            'position': position,
            'force_waiting_count': force_waiting_count,
            'open': open,
            'clearRates': clearRates,
            'tmp_rates_every_step': tmp_rates_every_step,
            'open_after_next_change': open_after_next_change
        }

    status = isChangeTo(df)
    ADXs = [float(x) for x in df[df.ADX == df.ADX]['ADX']][-200:]
    cfn_count = changeFromNowCount(df)
    dangerRate = getDangerRate(df)  # dangerRate的容忍度应该由earningRate决定，两个是正相关。能容忍利润做筹码，厌恶本金损失
    earningRate = 0
    pricePosis = getPricePosiArray(df)
    pricePosi = pricePosis[-1]
    if open != 0:
        if pricePosis[-2] == 0:
            earningRate = util.getRate(open, closes[-1])
        else:
            earningRate = util.getRate(closes[-1], open)

    # 趋势持续
    if status == 'STILL':
        # 止损止盈平仓
        if position != 0 and (
                (earningRate <= cond_er and dangerRate < -cond_before_er) or
                (earningRate > cond_er and dangerRate < -cond_after_er)
        ):
            position = 0
            clearRates.append(round((1 + earningRate / 100), 4))
            tmp_rates_every_step.append(earningRate)
            #print(str(tmp_rates_every_step.__len__()) + '@@@@@@@@@@tmp_rates_every_step: ' + str(tmp_rates_every_step))
            appendTreses(tmp_rates_every_step)
            tmp_rates_every_step = []
            print(nowTimeString + ':' + str(closes[-1]) + ' 止损止盈平仓 ### ### ### ### ### ### ### ### ### ### ### ### clear Position -> ' + str(earningRate) + ' r:' + str(
                reduce(lambda x, y: x * y, clearRates)))
            open = 0
            # open_after_next_change = True
            open_after_next_change = False
            # pushPosition(0)
        else:
            # 高位回落平仓后再此处等待，或瞬间变化时ADX条件不符合正在等待机会
            if position == 0:
                if open_after_next_change is False:
                    # 等到adx条件符合，开空仓
                    if pricePosi == 1 and (ADXs[-1] > adx_edge):
                        print(nowTimeString + ':' + str(closes[-1]) + ' 平仓后再此处等待 adx条件符合，开空仓 ### ### ### ### ### ### ### ### ### ### ### ### Down Position' + ' adx:' + str(ADXs[-1]))
                        position = -1
                        open = closes[-1]
                        dangerRate = 0
                    # 等到adx条件符合，开多仓
                    if pricePosi == 0 and (ADXs[-1] > adx_edge):
                        print(nowTimeString + ':' + str(closes[-1]) + ' 平仓后再此处等待 adx条件符合，开多仓 ### ### ### ### ### ### ### ### ### ### ### ### Up Position' + ' adx:' + str(ADXs[-1]))
                        position = 1
                        open = closes[-1]
                        dangerRate = 0
                else:
                    print(nowTimeString + ':' + " WAITING..." + ' adx: ' + str(ADXs[-1]))
            # 持有多仓
            if position > 0:
                print(nowTimeString + ':' + " Still Holding DUO..." + " dr:" + str(dangerRate) + ' er:' + str(
                    earningRate) + ' adx:' + str(ADXs[-1]))
                tmp_rates_every_step.append(earningRate)
            # 持有空仓
            if position < 0:
                print(nowTimeString + ':' + " Still Holding KON..." + " dr:" + str(dangerRate) + ' er:' + str(
                    earningRate) + ' adx:' + str(ADXs[-1]))
                tmp_rates_every_step.append(earningRate)


    # 瞬间 Down
    elif status == 'DOWN':
        # 前个趋势还在持仓，而现在趋势反转，应该反手做空
        if position != 0:
            position = 0
            clearRates.append(round((1 + earningRate / 100), 4))
            tmp_rates_every_step.append(earningRate)
            #print(str(tmp_rates_every_step.__len__()) + '@@@@@@@@@@tmp_rates_every_step: ' + str(tmp_rates_every_step))
            appendTreses(tmp_rates_every_step)
            tmp_rates_every_step = []
            print(nowTimeString + ': 趋势反转 ### ### ### ### ### ### ### ### ### ### ### ### clear Position ------> ' + str(earningRate) + ' r:' + str(
                reduce(lambda x, y: x * y, clearRates)))
            if ADXs[-1] < adx_edge: force_waiting_count = 5
            open = 0
        # -------------------------------------------------------------------
        # 变为Down瞬间，adx也符合要求，开空仓
        elif (ADXs[-1] > adx_edge and cfn_count < 10) and position == 0:
            print(nowTimeString + ':' + str(closes[-1]) + ' 变为Down瞬间，adx也符合要求，开空仓 ### ### ### ### ### ### ### ### ### ### ### ### Down Position' + ' adx:' + str(ADXs[-1]))
            position = -1
            open = closes[-1]
        # pushPosition(1)
        open_after_next_change = False

    # 瞬间 Up
    elif status == 'UP':
        # 前个趋势还在持仓，而现在趋势反转，应该反手做多
        if position != 0:
            position = 0
            clearRates.append(round((1 + earningRate / 100), 4))
            print(nowTimeString + ': 趋势反转 ### ### ### ### ### ### ### ### ### ### ### ### clear Position ------> ' + str(earningRate) + ' r:' + str(
                reduce(lambda x, y: x * y, clearRates)))
            tmp_rates_every_step.append(earningRate)
            #print(str(tmp_rates_every_step.__len__()) + '@@@@@@@@@@tmp_rates_every_step: ' + str(tmp_rates_every_step))
            appendTreses(tmp_rates_every_step)
            tmp_rates_every_step = []
            if ADXs[-1] < adx_edge: force_waiting_count = 5
            open = 0
            if earningRate > 2:
                print()
        # -------------------------------------------------------------------
        # 变为Up瞬间，adx也符合要求，开多仓
        elif (ADXs[-1] > adx_edge and cfn_count < 10) and position == 0:
            print(nowTimeString + ':' + str(closes[-1]) + ' 变为Up瞬间，adx也符合要求，开多仓 ### ### ### ### ### ### ### ### ### ### ### ### Up Position' + ' adx:' + str(ADXs[-1]))
            position = 1
            open = closes[-1]
        open_after_next_change = False
        # pushPosition(-1)
    if clearRates.__len__() > 500:
        clearRates.pop(0)
    return {
        'df': df,
        'position': position,
        'force_waiting_count': force_waiting_count,
        'open': open,
        'clearRates': clearRates,
        'tmp_rates_every_step': tmp_rates_every_step,
        'open_after_next_change': open_after_next_change
    }


def trade(strategyTemplate):
    pass


def action(msg):
    ts = util.string2timestamp(str(nowTimeString))
    frequencyLimitFlag = int(time.strftime('%M', time.localtime(ts))) % int(frequency[0:-1]) == 0
    if frequencyLimitFlag is False:
        return msg
    if util.isFutureTradingTime(nowTimeString=nowTimeString) is False or util.isFutureCommonTradingTime(
            security=security,
            nowTimeString=nowTimeString) is False:
        return msg
    msg = loop(security=security, frequency=frequency, nowTimeString=nowTimeString, msg=msg)
    return msg


removeTreses()
for nowTimeString in timeArr:
    msg = action(msg=msg)

#
# class MyStrategy(CtaTemplate):
#     author = 'nobody'
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
#         super(MyStrategy, self).__init__(
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
