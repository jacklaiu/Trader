import talib
import jqdatasdk
import numpy as np
import PyBase.Util as util
import time
from functools import reduce

markTreses = False

cond_er = 0.4
cond_before_er = 0.8
cond_after_er = 0.8
adx_timeperiod = 4

real_open_rate = 0.2

adx_edge = 40
fast_ema = 6
slow_ema = 23

# RB8888.XSGE
# JD8888.XDCE
# HC8888.XSGE
# MA8888.XZCE
# TA8888.XZCE
# AP8888.XZCE

frequency = '28m'

security = None


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

removeTreses()

def appendTreses(tmp_rates_every_step):
    tmp_treses = util.getProperty('tmp_treses')
    if tmp_treses is not None:
        tmp_treses.append(tmp_rates_every_step)
    else:
        tmp_treses = [tmp_rates_every_step]
    if markTreses is True:
        util.setProperty('tmp_treses', tmp_treses)

def loop(security=None, frequency=None, nowTimeString=None, msg=None):
    df = msg.get('df')
    position = msg.get('position')
    force_waiting_count = msg.get('force_waiting_count')
    open = msg.get('open')
    real_open = msg.get('real_open')
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
    if open is not None and open != 0:
        if pricePosis[-2] == 0:
            earningRate = util.getRate(open, closes[-1])
        else:
            earningRate = util.getRate(closes[-1], open)
    if real_open is not None and real_open != 0:
        if pricePosis[-2] == 0:
            earningRate = util.getRate(real_open, closes[-1])
        else:
            earningRate = util.getRate(closes[-1], real_open)

    # 趋势持续
    if status == 'STILL':
        # 止损止盈平仓
        if position != 0 and (
                (earningRate <= cond_er and dangerRate < -cond_before_er) or
                (earningRate > cond_er and dangerRate < -cond_after_er)
        ):
            if real_open != 0:
                clearRates.append(round((1 + earningRate / 100), 4))
            else:
                clearRates.append(1)
            tmp_rates_every_step.append(earningRate)
            #print(str(tmp_rates_every_step.__len__()) + '@@@@@@@@@@tmp_rates_every_step: ' + str(tmp_rates_every_step))
            appendTreses(tmp_rates_every_step)
            tmp_rates_every_step = []
            print('!***********************# clear Position 止损止盈平仓 -> ' + str(earningRate) + ' r:' + str(
                reduce(lambda x, y: x * y, clearRates)) + '!!! ----- !!!')
            position = 0
            open = 0
            real_open = 0
            # open_after_next_change = True
            open_after_next_change = False
            # pushPosition(0)
        else:
            # 高位回落平仓后再此处等待，或瞬间变化时ADX条件不符合正在等待机会
            if position == 0:
                if open_after_next_change is False:
                    # 等到adx条件符合，开空仓
                    if pricePosi == 1 and (ADXs[-1] > adx_edge):
                        print(' 平仓后再此处等待 adx条件符合，开空仓 ### ### ### ### ### ### ### ### ### ### ### ### Down Position' + ' adx:' + str(ADXs[-1]))
                        position = -1
                        open = closes[-1]
                        dangerRate = 0
                    # 等到adx条件符合，开多仓
                    elif pricePosi == 0 and (ADXs[-1] > adx_edge):
                        print(' 平仓后再此处等待 adx条件符合，开多仓 ### ### ### ### ### ### ### ### ### ### ### ### Up Position' + ' adx:' + str(ADXs[-1]))
                        position = 1
                        open = closes[-1]
                        dangerRate = 0
                    else:
                        print(nowTimeString + ':' + " WAITING..." + ' close: ' + str(closes[-1]))
                else:
                    print(nowTimeString + ':' + " WAITING..." + ' adx: ' + str(ADXs[-1]))
            # 持有多仓
            if position > 0:
                print(nowTimeString + ':' + " Still Holding DUO..." + " dr:" + str(dangerRate) + ' er:' + str(
                    earningRate) + ' adx:' + str(ADXs[-1]))
                tmp_rates_every_step.append(earningRate)
                if earningRate > real_open_rate and real_open == 0:
                    closes = closes[-100:]
                    real_open = closes[-1]
                    print('!***********************#正式做多：' + str(closes[-1]))
            # 持有空仓
            if position < 0:
                print(nowTimeString + ':' + " Still Holding KON..." + " dr:" + str(dangerRate) + ' er:' + str(
                    earningRate) + ' adx:' + str(ADXs[-1]))
                tmp_rates_every_step.append(earningRate)
                if earningRate > real_open_rate and real_open == 0:
                    real_open = closes[-1]
                    print('!***********************#正式做空：' + str(closes[-1]))

    # 瞬间 Down
    elif status == 'DOWN':
        # 前个趋势还在持仓，而现在趋势反转，应该反手做空
        if position != 0:
            position = 0
            if real_open != 0:
                clearRates.append(round((1 + earningRate / 100), 4))
            else:
                clearRates.append(1)
            tmp_rates_every_step.append(earningRate)
            #print(str(tmp_rates_every_step.__len__()) + '@@@@@@@@@@tmp_rates_every_step: ' + str(tmp_rates_every_step))
            appendTreses(tmp_rates_every_step)
            tmp_rates_every_step = []
            print(nowTimeString + ':!***********************# clear Position 趋势反转 ------> ' + str(earningRate) + ' r:' + str(
                reduce(lambda x, y: x * y, clearRates)) + '!!! ----- !!!')
            if ADXs[-1] < adx_edge: force_waiting_count = 5
            open = 0
            real_open = 0
        # -------------------------------------------------------------------
        # 变为Down瞬间，adx也符合要求，开空仓
        elif (ADXs[-1] > adx_edge and cfn_count < 10) and position == 0:
            print(' 变为Down瞬间，adx也符合要求，开空仓 ### ### ### ### ### ### ### ### ### ### ### ### Down Position' + ' adx:' + str(ADXs[-1]))
            position = -1
            open = closes[-1]
        # pushPosition(1)
        open_after_next_change = False

    # 瞬间 Up
    elif status == 'UP':
        # 前个趋势还在持仓，而现在趋势反转，应该反手做多
        if position != 0:
            position = 0
            if real_open != 0:
                clearRates.append(round((1 + earningRate / 100), 4))
            else:
                clearRates.append(1)
            print(nowTimeString + ':!***********************# clear Position 趋势反转 ------> ' + str(earningRate) + ' r:' + str(
                reduce(lambda x, y: x * y, clearRates)) + '!!! ----- !!!')
            tmp_rates_every_step.append(earningRate)
            #print(str(tmp_rates_every_step.__len__()) + '@@@@@@@@@@tmp_rates_every_step: ' + str(tmp_rates_every_step))
            appendTreses(tmp_rates_every_step)
            tmp_rates_every_step = []
            if ADXs[-1] < adx_edge: force_waiting_count = 5
            open = 0
            real_open = 0
            if earningRate > 2:
                print()
        # -------------------------------------------------------------------
        # 变为Up瞬间，adx也符合要求，开多仓
        elif (ADXs[-1] > adx_edge and cfn_count < 10) and position == 0:
            print(' 变为Up瞬间，adx也符合要求，开多仓 ### ### ### ### ### ### ### ### ### ### ### ### Up Position' + ' adx:' + str(ADXs[-1]))
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
        'real_open': real_open,
        'clearRates': clearRates,
        'tmp_rates_every_step': tmp_rates_every_step,
        'open_after_next_change': open_after_next_change
    }


def trade(strategyTemplate):
    pass

def _handleOneTick(msg=None, nowTimeString=None):

    if security is None:
        print('请确认Security')

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

class TickHandler():

    def __init__(self):
        self.msg = {
            'df': None,
            'position': 0,
            'force_waiting_count': 0,
            'open': 0,
            'clearRates': [],
            'tmp_rates_every_step': [],
            'open_after_next_change': False,
            'real_open': 0
        }

    def handleOneTick(self, nowTimeString=None):
        self.msg = _handleOneTick(msg=self.msg, nowTimeString=nowTimeString)


