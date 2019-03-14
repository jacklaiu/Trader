# encoding: UTF-8

import jqdatasdk
import numpy as np
import time
import talib
from Status import Status
import math
import Util as util
from numpy import int32
import Dao as dao

class DoubleEMaStrategyBase:

    def __init__(self, security='RB1901.XSGE', status=Status(), ctaTemplate=None, enableTrade=False,
                 frequency='4m', pricePosi_top=0, pricePosi_bottom=1,
                 dayStartTime='09:00:20', dayEndTime='10:14:00',
                 noonStartTime='10:30:00', noonEndTime='11:29:00',
                 afternoonStartTime='13:30:00', afternoonEndTime='14:59:00',
                 nightStartTime='21:00:00', nightEndTime='22:59:00',
                 jqDataAccount='13268108673', jqDataPassword='king20110713'):
        self.enableTrade = enableTrade
        self.ctaTemplate = ctaTemplate
        self.status = status
        self.jqDataAccount = jqDataAccount
        self.jqDataPassword = jqDataPassword
        # self.jqDataAccount = '13824472562'
        # self.jqDataPassword = '472562'
        self.frequency = frequency
        self.dataRow = 200
        self.pricePosi_top = pricePosi_top
        self.pricePosi_bottom = pricePosi_bottom
        self.lastExeTime = None
        self.security = security
        self.pricePositions = []
        self.maxPosition = dao.readMaxPosition(security)
        self.duo_position = dao.readDuoPosition(security) # 多单持仓手数
        self.kong_position = dao.readKongPosition(security) # 空单持仓手数

        self.writeCtaLog('########################jqdata账号：' + str(self.jqDataAccount))
        self.writeCtaLog('########################合约代码：' + str(self.security))
        self.writeCtaLog('########################多单持仓：' + str(self.duo_position))
        self.writeCtaLog('########################空单持仓：' + str(self.kong_position))
        self.writeCtaLog('########################最大持仓：' + str(self.maxPosition))
        self.writeCtaLog('########################策略级别：' + str(self.frequency))
        self.writeCtaLog('########################允许交易：' + str(self.enableTrade))
        self.writeCtaLog('########################单次获取数据行：' + str(self.dataRow))
        self.writeCtaLog('########################EMA5-Posi-top：' + str(self.pricePosi_top))
        self.writeCtaLog('########################EMA5-Posi-bottom：' + str(self.pricePosi_bottom))

        self.dayStartTime = dayStartTime
        self.dayEndTime = dayEndTime
        self.noonStartTime = noonStartTime
        self.noonEndTime = noonEndTime
        self.afternoonStartTime = afternoonStartTime
        self.afternoonEndTime = afternoonEndTime
        self.nightStartTime = nightStartTime
        self.nightEndTime = nightEndTime

    def _isTradingTime(self, currentTimeForTesting):
        if currentTimeForTesting is None:
            now = time.strftime('%H:%M:%S',time.localtime(time.time()))
        else:
            ts = util.string2timestamp(currentTimeForTesting)
            now = time.strftime('%H:%M:%S', time.localtime(ts))
        if now >= self.dayStartTime and now <= self.dayEndTime:
            return True
        if now >= self.afternoonStartTime and now <= self.afternoonEndTime:
            return True
        if now >= self.noonStartTime and now <= self.noonEndTime:
            return True
        if now >= self.nightStartTime and now <= self.nightEndTime:
            return True
        return False

    def _shouldStartJudge(self, currentTimeForTesting=None):
        currentTimestamp = time.time() * 1000
        isTradingTime = self._isTradingTime(currentTimeForTesting)
        if currentTimeForTesting is not None:
            ts  = util.string2timestamp(currentTimeForTesting)
            frequencyLimitFlag = int(time.strftime('%M', time.localtime(ts))) % int(self.frequency[0:-1]) == 0
            currentTimestamp = util.string2timestamp(currentTimeForTesting) * 1000
        else:
            n = int(time.strftime('%M', time.localtime(currentTimestamp/1000))) % int(self.frequency[0:-1])
            frequencyLimitFlag = n == 0

        if isTradingTime is True and self.lastExeTime is None: # 第一次
            if frequencyLimitFlag is True:
                self.lastExeTime = currentTimestamp
                return True
            else:
                return False

        elif isTradingTime is True and currentTimestamp - self.lastExeTime > 66 * 1000: # 当前时间已经距离上次调用更新状态过了self.waittime分钟，可以再次调用
            if frequencyLimitFlag is True:
                self.lastExeTime = currentTimestamp
                return True
            else:
                return False
        return False

    def startJudgeAndRefreshStatus(self, currentTimeForTesting=None):
        self.pricePositions = []
        if self._shouldStartJudge(currentTimeForTesting) is False:
            return False
        if self.enableTrade:
            time.sleep(19)
        jqdatasdk.auth(self.jqDataAccount, self.jqDataPassword)
        nowTimeString = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
        if currentTimeForTesting is not None:
            nowTimeString = currentTimeForTesting
        self.df = jqdatasdk.get_price(security=self.security, count=self.dataRow, end_date=nowTimeString, frequency=self.frequency,
                                      fields=['close'])
        close = [float(x) for x in self.df['close']]
        self.df['EMA5'] = talib.EMA(np.array(close), timeperiod=5)
        self.df['EMA10'] = talib.EMA(np.array(close), timeperiod=10)
        self.df['EMA20'] = talib.EMA(np.array(close), timeperiod=20)
        self.indexList = self.df[self.df.EMA10 == self.df.EMA10].index.tolist()
        for index in self.indexList:
            ema5 = self.df.loc[index, 'EMA5']
            ema10 = self.df.loc[index, 'EMA10']
            emas = sorted([ema5, ema10], reverse=True)
            pricePosi = 0
            for ema in emas:
                if ema == ema5:
                    break
                pricePosi = pricePosi + 1

            self.pricePositions.append(pricePosi)

        self._refreshStatus(nowTimeString)
        return True

    def _refreshStatus(self, nowTimeString=None): # lockingbuy lockingshort holdingbuy holdingshort waiting
        df = self.df
        count = 0
        index = None
        # 保证最新的数据是符合frequency的，因为需要保证数据的连续性
        lastIndex = self.indexList[-1]
        ts = util.string2timestamp(str(lastIndex))
        frequencyLimitFlag = int(time.strftime('%M', time.localtime(ts))) % int(self.frequency[0:-1]) == 0
        if frequencyLimitFlag is False:
            return
        #------------------------------------------
        for pricePosi in self.pricePositions:
            _status = self.status.status
            _buyStartClose = self.status.buyStartClose
            _shortStartClose = self.status.shortStartClose
            _lockClose = self.status.lockClose
            try:
                index = self.indexList[count]
            except:
                print

            price = df.loc[index, 'close']

            # status == waiting不会触发状态
            if self.status.status == 'holdingbuy' or self.status.status == 'holdingshort': # or self.status.status == 'lockingbuy' or self.status.status == 'lockingshort':

                if self.status.status == 'holdingbuy': # or self.status.status == 'lockingbuy':
                    # 平仓点
                    if (self.getLifeEMAK() < 1 and self.getEMADistance() > 0.1) or self.isLossing() is True:
                        self.status.lockClose = 0
                        self.status.buyStartClose = 0
                        self.status.shortStartClose = 0
                        self.status.preStatus = self.status.status
                        self.status.status = 'waiting'

                elif self.status.status == 'holdingshort':# or self.status.status == 'lockingshort':
                    # 平仓点
                    if (self.getLifeEMAK() > -1 and self.getEMADistance() > 0.1) or self.isLossing() is True:
                        self.status.lockClose = 0
                        self.status.buyStartClose = 0
                        self.status.shortStartClose = 0
                        self.status.preStatus = self.status.status
                        self.status.status = 'waiting'

                count = count + 1
                continue

            # 开多仓
            # if self.getLifeEMAK() > 6 \
            #         and pricePosi == 0 \
            #         and self.getEMADistance() < 0.1 or \
            #         (self.getEMADistance(preCount=0) < 0.1
            #          and self.getEMADistance(preCount=1) < 0.1
            #          and self.getEMADistance(preCount=2) < 0.1
            #          and self.getLifeEMAK() > 2):

            ed0 = self.getEMADistance(preCount=0)
            ed1 = self.getEMADistance(preCount=1)
            ed2 = self.getEMADistance(preCount=2)
            lemk0 = self.getLifeEMAK(preCount=0)
            # lemk1 = self.getLifeEMAK(preCount=1)


            if (ed0 < 0.1 and ed1 < 0.1 and ed2 < 0.1 and lemk0 > 2):
            # if pricePosi == 0:
                self.status.lockClose = 0
                self.status.buyStartClose = price
                self.status.shortStartClose = 0
                self.status.preStatus = self.status.status
                self.status.status = 'holdingbuy'

            # 开空仓
            # if self.getLifeEMAK() < -6 \
            #         and pricePosi == 1 \
            #         and self.getEMADistance() < 0.1 or \
            #         (self.getEMADistance(preCount=0) < 0.1
            #          and self.getEMADistance(preCount=1) < 0.1
            #          and self.getEMADistance(preCount=2) < 0.1
            #          and self.getLifeEMAK() < -2):

            if (ed0 < 0.1 and ed1 < 0.1 and ed2 < 0.1 and lemk0 < -2):
            #if pricePosi == 1:
                self.status.lockClose = 0
                self.status.buyStartClose = 0
                self.status.shortStartClose = price
                self.status.preStatus = self.status.status
                self.status.status = 'holdingshort'

            count = count + 1

        flag = 'x'
        if self.isHoldingShort() or self.isHoldingBuy():
            flag = '√√√√√√√√√√√√√√√√√√√√√√√√√'
        emak = self.getLifeEMAK()
        if emak is None:
            print
        self.writeCtaLog('时刻[' + nowTimeString + ']开始:  -> status(now): ' + str(self.status.status)
                         + ' -> EMAk:' + str(emak)
                         + ' -> Holding:' + str(flag)
                         + ' -> distanceRate:' + str(self.getEMADistance()))


    def isLossing(self):
        if self.status.status == 'holdingbuy':
            nowPrice = float(self.df.loc[self.indexList[-1], 'close'])
            if round((nowPrice - self.status.buyStartClose) / self.status.buyStartClose, 2)*100 < -0.3:
                return True
            else:
                return False
        if self.status.status == 'holdingshort':
            nowPrice = float(self.df.loc[self.indexList[-1], 'close'])
            if round((self.status.shortStartClose - nowPrice) / self.status.shortStartClose, 2)*100 < -0.3:
                return True
            else:
                return False

    def getLifeEMAK(self, preCount=0):
        f = self.getEMAK(ematype='5', preCount=preCount)
        t = self.getEMAK(ematype='10', preCount=preCount)
        return f+t

    def getEMADistance(self, ematypes=('5', '20'), preCount=0):
        values = []
        for ematype in ematypes:
            values.append(float(self.df.loc[self.indexList[-1 - preCount], 'EMA' + ematype]))
        preV = None
        firstV = None
        distance = 0
        for value in values:
            if firstV is None:
                firstV = value
            if preV is not None:
                distance = distance + abs(value - preV)
            preV = value
        return round(distance/ematypes.__len__()/firstV, 8) * 100

    def getLifeEMAK_Serial(self):
        f = self.getEMAK(ematype='5', preCount=0) * 0.6 + self.getEMAK(ematype='5', preCount=1) * 0.6 + self.getEMAK(ematype='5', preCount=2) * 0.6
        t = self.getEMAK(ematype='10', preCount=0) + self.getEMAK(ematype='10', preCount=1) + self.getEMAK(ematype='10', preCount=2)
        return f+t

    def getEMAK(self, preCount=0, ematype='5'):
        ema_1 = float(self.df.loc[self.indexList[-1-preCount], 'EMA' + ematype])
        a = ema_1 / 1000
        ema_2 = float(self.df.loc[self.indexList[-2-preCount], 'EMA' + ematype])
        return (ema_1 - ema_2) / a * 3

    # def isEMA_speedUp(self, ematype='5'):
    #     v0 = self.getEMAK(0, ematype)
    #     v1 = self.getEMAK(1, ematype)
    #     v2 = self.getEMAK(2, ematype)
    #     if v0 > v1 and v1 > v2:
    #         return True
    #     else:
    #         return False
    #
    # def isEMA_speedDown(self, ematype='5'):
    #     v0 = self.getEMAK(0, ematype)
    #     v1 = self.getEMAK(1, ematype)
    #     v2 = self.getEMAK(2, ematype)
    #     if v2 > v1 and v1 > v0:
    #         return True
    #     else:
    #         return False

    def buy(self, tick):
        preStatus = self.status.preStatus
        status = self.status.status
        if status != 'holdingbuy':
            return
        if preStatus == 'waiting' and self.isWait() is True and self.isHoldingBuy() is False:
            if self.enableTrade is True:
                self.ctaTemplate.buy(tick.upperLimit, int32(self.maxPosition))
                time.sleep(5)
            self.writeCtaLog('开多' + str(self.maxPosition) + '手')
            self.duo_position = self.maxPosition
            self.writeCtaLog('############################################多单持仓：' + str(self.duo_position) + ' 空单持仓：' + str(self.kong_position))
            dao.updatePosition(self.duo_position, self.kong_position, self.security)

        if preStatus == 'holdingshort' and self.isWait() is False and self.isHoldingShort() is True:
            if self.enableTrade is True:
                self.ctaTemplate.cover(tick.upperLimit, int32(self.maxPosition))
                time.sleep(5)
            self.writeCtaLog('平空' + str(self.maxPosition) + '手')
            self.kong_position = 0
            self.writeCtaLog('############################################多单持仓：' + str(self.duo_position) + ' 空单持仓：' + str(self.kong_position))
            dao.updatePosition(self.duo_position, self.kong_position, self.security)

            if self.enableTrade is True:
                self.ctaTemplate.buy(tick.upperLimit, int32(self.maxPosition))
                time.sleep(5)
            self.writeCtaLog('开多' + str(self.maxPosition) + '手')
            self.duo_position = self.maxPosition
            self.writeCtaLog('############################################多单持仓：' + str(self.duo_position) + ' 空单持仓：' + str(self.kong_position))
            dao.updatePosition(self.duo_position, self.kong_position, self.security)


    def short(self, tick):
        preStatus = self.status.preStatus
        status = self.status.status
        if status != 'holdingshort':
            return
        if preStatus == 'waiting' and self.isWait() is True and self.isHoldingShort() is False:
            if self.enableTrade is True:
                self.ctaTemplate.short(tick.lowerLimit, int32(self.maxPosition))
                time.sleep(5)
            self.writeCtaLog('开空' + str(self.maxPosition) + '手')
            self.kong_position = self.maxPosition
            self.writeCtaLog('############################################多单持仓：' + str(self.duo_position) + ' 空单持仓：' + str(self.kong_position))
            dao.updatePosition(self.duo_position, self.kong_position, self.security)

        if preStatus == 'holdingbuy'  and self.isWait() is False and self.isHoldingShort() is False:
            if self.enableTrade is True:
                self.ctaTemplate.sell(tick.lowerLimit, int32(self.maxPosition))
                time.sleep(5)
            self.writeCtaLog('平多' + str(self.maxPosition) + '手')
            self.duo_position = 0
            self.writeCtaLog('############################################多单持仓：' + str(self.duo_position) + ' 空单持仓：' + str(self.kong_position))
            dao.updatePosition(self.duo_position, self.kong_position, self.security)

            if self.enableTrade is True:
                self.ctaTemplate.short(tick.lowerLimit, int32(self.maxPosition))
                time.sleep(5)
            self.writeCtaLog('开空' + str(self.maxPosition) + '手')
            self.kong_position = self.maxPosition
            self.writeCtaLog('############################################多单持仓：' + str(self.duo_position) + ' 空单持仓：' + str(self.kong_position))
            dao.updatePosition(self.duo_position, self.kong_position, self.security)

    def closePosition(self, tick):
        preStatus = self.status.preStatus
        status = self.status.status
        if status == 'waiting' and self.isWait() is False and self.isHoldingBuy() is True:
            if self.enableTrade is True:
                self.ctaTemplate.sell(tick.lowerLimit, int32(self.maxPosition)) # 平多
                time.sleep(5)
            self.writeCtaLog('平多' + str(self.maxPosition) + '手')
            self.duo_position = 0
            self.kong_position = 0
            dao.updatePosition(self.duo_position, self.kong_position, self.security)
            self.writeCtaLog(
                '############################################多单持仓：' + str(self.duo_position) + ' 空单持仓：' + str(
                    self.kong_position))

        if status == 'waiting' and self.isWait() is False and self.isHoldingShort() is True:
            if self.enableTrade is True:
                self.ctaTemplate.cover(tick.upperLimit, int32(self.maxPosition)) # 平空
                time.sleep(5)
            self.writeCtaLog('平空' + str(self.maxPosition) + '手')
            self.duo_position = 0
            self.kong_position = 0
            dao.updatePosition(self.duo_position, self.kong_position, self.security)
            self.writeCtaLog(
                '############################################多单持仓：' + str(self.duo_position) + ' 空单持仓：' + str(
                    self.kong_position))

    # def lock(self, tick):
    #     preStatus = self.status.preStatus
    #     status = self.status.status
        # if preStatus == 'holdingbuy' and status == 'lockingbuy' and self.isHoldingBuy() is True: # 锁多仓
        #     if self.enableTrade is True:
        #         self.ctaTemplate.sell(tick.lowerLimit, int32(self.maxPosition))  # 平多
        #     self.writeCtaLog('平' + str(self.maxPosition) + '手')
        #     self.duo_position = 0
        #     self.kong_position = 0
        #     self.writeCtaLog('############################################多单持仓：' + str(self.duo_position) + ' 空单持仓：' + str(self.kong_position))
        #     dao.updatePosition(self.duo_position, self.kong_position, self.security)
        #
        # if preStatus == 'holdingshort' and status == 'lockingshort' and self.isHoldingShort() is True: # 锁空仓
        #     if self.enableTrade is True:
        #         self.ctaTemplate.cover(tick.upperLimit, int32(self.maxPosition))  # 平空
        #     self.writeCtaLog('平' + str(self.maxPosition) + '手')
        #     self.duo_position = 0
        #     self.kong_position = 0
        #     self.writeCtaLog('############################################多单持仓：' + str(self.duo_position) + ' 空单持仓：' + str(self.kong_position))
        #     dao.updatePosition(self.duo_position, self.kong_position, self.security)

    # def unlock(self, tick):
    #     preStatus = self.status.preStatus
    #     status = self.status.status
        # if preStatus == 'lockingbuy' and status == 'holdingbuy' and self.isWait() is True:
        #     if self.enableTrade is True:
        #         self.ctaTemplate.buy(tick.upperLimit, int32(self.maxPosition))
        #     self.writeCtaLog('开多' + str(self.maxPosition) + '手')
        #     self.duo_position = self.maxPosition
        #     self.kong_position = 0
        #     self.writeCtaLog('############################################多单持仓：' + str(self.duo_position) + ' 空单持仓：' + str(self.kong_position))
        #     dao.updatePosition(self.duo_position, self.kong_position, self.security)
        #
        # if preStatus == 'lockingshort' and status == 'holdingshort' and self.isWait() is True:
        #     if self.enableTrade is True:
        #         self.ctaTemplate.short(tick.upperLimit, int32(self.maxPosition))
        #     self.writeCtaLog('开空' + str(self.maxPosition) + '手')
        #     self.duo_position = 0
        #     self.kong_position = self.maxPosition
        #     self.writeCtaLog('############################################多单持仓：' + str(self.duo_position) + ' 空单持仓：' + str(self.kong_position))
        #     dao.updatePosition(self.duo_position, self.kong_position, self.security)

    def trade(self, tick):
        self.buy(tick)
        self.short(tick)
        self.closePosition(tick)
        # self.lock(tick)
        # self.unlock(tick)

    def isLock(self):
        duo = self.duo_position
        kon = self.kong_position
        if duo == kon:
            return True
        else:
            return False

    def isWait(self):
        duo = self.duo_position
        kon = self.kong_position
        if duo == 0 and kon == 0:
            return True
        return False

    def isHoldingBuy(self):
        duo = self.duo_position
        max = self.maxPosition
        if duo == max:
            return True
        return False

    def isHoldingShort(self):
        kon = self.kong_position
        max = self.maxPosition
        if kon == max:
            return True
        return False

    def writeCtaLog(self, content):
        if self.ctaTemplate is None:
            print content
        else:
            self.ctaTemplate.writeCtaLog(u'' + content)
            print content



