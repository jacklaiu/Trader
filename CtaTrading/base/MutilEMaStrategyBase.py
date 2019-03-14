# encoding: UTF-8

import jqdatasdk
import numpy as np
import time
import talib
from Status import Status
import Util as util
from numpy import int32
import Dao as dao
import base.FutureTimeDict as fm
import base.ProgramAndMe_ConnectionUnit as pamConn
import base.MutilEMAStrategyBaseHelper as msbh
import base.SmtpClient as smtpClient

class MutilEMaStrategyBase:

    def __init__(self, security=None, status=Status(), ctaTemplate=None, controlRisk=None,
                 enableTrade=False, enableBuy=True, enableShort=True, frequency=None,
                 pricePosi_top = 0, pricePosi_bottom = 4,
                 jqDataAccount='13268108673', jqDataPassword='king20110713'):
        futureMsg = fm.getFutureMsg(security)
        self.enableTrade = enableTrade
        self.enableBuy = enableBuy
        self.enableShort = enableShort
        self.ctaTemplate = ctaTemplate
        self.controlRisk = controlRisk
        self.status = status
        self.jqDataAccount = jqDataAccount
        self.jqDataPassword = jqDataPassword
        self.frequency = frequency

        self.dataRow = 100
        self.pricePosi_top = pricePosi_top
        self.pricePosi_bottom = pricePosi_bottom
        self.lastExeTime = None
        self.security = security
        self.pricePositions = []
        self.maxPosition = dao.readMaxPosition(security)
        self.duo_position = dao.readDuoPosition(security) # 多单持仓手数
        self.kong_position = dao.readKongPosition(security) # 空单持仓手数

        self.writeCtaLog('########################允许交易：' + str(self.enableTrade))
        self.writeCtaLog('########################开多：' + str(self.enableBuy))
        self.writeCtaLog('########################开空：' + str(self.enableShort))
        self.writeCtaLog('########################合约代码：' + str(self.security))
        self.writeCtaLog('########################多单持仓：' + str(self.duo_position))
        self.writeCtaLog('########################空单持仓：' + str(self.kong_position))
        self.writeCtaLog('########################最大持仓：' + str(self.maxPosition))
        self.writeCtaLog('########################策略级别：' + str(self.frequency))
        self.writeCtaLog('########################jqdata账号：' + str(self.jqDataAccount))

        self.dayStartTime = futureMsg['dayStartTime']
        self.dayEndTime = futureMsg['dayEndTime']
        self.noonStartTime = futureMsg['noonStartTime']
        self.noonEndTime = futureMsg['noonEndTime']
        self.afternoonStartTime = futureMsg['afternoonStartTime']
        self.afternoonEndTime = futureMsg['afternoonEndTime']
        try :
            self.nightStartTime = futureMsg['nightStartTime']
            self.nightEndTime = futureMsg['nightEndTime']
        except:
            self.nightStartTime = None
            self.nightEndTime = None

        self.isInit = True
        self.rate = 1
        self.openPrice = None

    def getAdvancedData(self, nowTimeString):
        newRow = None
        newIndex = None
        df = None
        if self.isInit is True:
            df = jqdatasdk.get_price(
                security=self.security,
                count=self.dataRow,
                end_date=nowTimeString[0:nowTimeString.rindex(':') + 1] + '30',
                frequency=self.frequency,
                fields=['close', 'open', 'volume', 'high', 'low', 'money']
            )
        else:
            newDf = jqdatasdk.get_price(
                security=self.security,
                count=1,
                end_date=nowTimeString[0:nowTimeString.rindex(':') + 1] + '30',
                frequency=self.frequency,
                fields=['close', 'open', 'volume']
            )
            newIndex = newDf.index.tolist()[0]
            newRow = newDf.loc[newIndex]
        if newRow is not None:
            df.loc[newIndex] = newRow
        close = [float(x) for x in df['close']]
        df['EMA5'] = talib.EMA(np.array(close), timeperiod=5)
        df['EMA10'] = talib.EMA(np.array(close), timeperiod=10)
        df['EMA20'] = talib.EMA(np.array(close), timeperiod=20)
        df['EMA40'] = talib.EMA(np.array(close), timeperiod=40)
        df['EMA60'] = talib.EMA(np.array(close), timeperiod=60)
        df['MA5'] = talib.MA(np.array(close), timeperiod=5)
        df['MA10'] = talib.MA(np.array(close), timeperiod=10)
        df['MA20'] = talib.MA(np.array(close), timeperiod=20)
        df['MA40'] = talib.MA(np.array(close), timeperiod=40)
        df['MA60'] = talib.MA(np.array(close), timeperiod=60)
        df.drop([df.index.tolist()[0]], inplace=True)
        return df

    def getPricePosiArray(self):
        pricePositions = []
        for index in self.indexList:
            ema5 = self.df.loc[index, 'EMA5']
            emas = sorted(
                [ema5, self.df.loc[index, 'EMA10'], self.df.loc[index, 'EMA20'], self.df.loc[index, 'EMA40'],
                 self.df.loc[index, 'EMA60']],
                reverse=True)
            pricePosi = 0
            for ema in emas:
                if ema == ema5:
                    break
                pricePosi = pricePosi + 1
            pricePositions.append(pricePosi)
        return pricePositions

    def getIndexList(self):
        return self.df[self.df.EMA60 == self.df.EMA60].index.tolist()

    def getNowTimeString(self, currentTimeForTesting = None):
        nowTimeString = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        if currentTimeForTesting is not None:
            nowTimeString = currentTimeForTesting
        return nowTimeString

    def refreshStatus(self, nowTimeString=None): # lockingbuy lockingshort holdingbuy holdingshort waiting
        # 保证最新的数据是符合frequency的，因为需要保证数据的连续性
        ts = util.string2timestamp(str(self.indexList[-1]))
        frequencyLimitFlag = int(time.strftime('%M', time.localtime(ts))) % int(self.frequency[0:-1]) == 0
        if frequencyLimitFlag is True:
            count = 0
            self.lastestAbsK = None
            for pricePosi in self.pricePositions:
                index = self.indexList[count]
                self.now_ema5 = self.df['EMA5'][index]
                self.now_ema10 = self.df['EMA10'][index]
                self.now_ema20 = self.df['EMA10'][index]
                self.now_pricePosi = pricePosi
                self.now_price = self.df.loc[index, 'close']
                self.doRefresh(count, nowTimeString)
                count = count + 1

        _emak60 = self.getEMAK(ematype='60', preCount=0) * 100
        self.writeCtaLog('[' + nowTimeString + ']: preStatus: ' + str(self.status.preStatus)
                         + ' -> status(now): ' + self.status.status
                         + ' -> va(now): ' + str(self.getVolumeArrow(indexCount=None))
                         + ' -> ha(now): ' + str(self.getHighPriceArrow(indexCount=None))
                         + ' -> la(now): ' + str(self.getLowPriceArrow(indexCount=None))
                         + ' -> lemak(now): ' + str(self.getLifeEMAK(indexCount=None))
                         + ' -> priceposi(now): ' + str(self.now_pricePosi)
                         )

    def doRefresh(self, indexCount, nowTimeString):
        # status == waiting不会触发状态
        if self.status.status == 'holdingbuy' or self.status.status == 'holdingshort':
            # 爆量通知
            if indexCount == self.indexList.__len__() - 1 and \
                    self.getVolumeArrow(indexCount=indexCount) > 10 and \
                    (self.getLowPriceArrow(indexCount=indexCount) > 20 or self.getHighPriceArrow(indexCount=indexCount) > 20):
                smtpClient.notifyVolumeUnusual(security=self.security)
                time.sleep(1)

            if self.status.status == 'holdingbuy':
                # 平仓点
                if self.now_pricePosi != self.pricePosi_top:
                    self.status.lockClose = 0
                    self.status.buyStartClose = 0
                    self.status.shortStartClose = 0
                    self.status.preStatus = self.status.status
                    self.status.status = 'waiting'
                    if indexCount == self.indexList.__len__() - 1 and self.openPrice is not None:
                        smtpClient.notifyCloseDuo(security=self.security, currentTimeString=nowTimeString)
                        self.rate = self.rate * (1+round((self.now_price - self.openPrice)/self.openPrice,4)) * (0.9996) * (0.9996)
                        print "$$$$$$$$$$$$Rate:" + str(self.rate)
                        time.sleep(1)

            elif self.status.status == 'holdingshort':
                # 平仓点
                if self.now_pricePosi != self.pricePosi_bottom:
                    self.status.lockClose = 0
                    self.status.buyStartClose = 0
                    self.status.shortStartClose = 0
                    self.status.preStatus = self.status.status
                    self.status.status = 'waiting'
                    if indexCount == self.indexList.__len__() - 1 and self.openPrice is not None:
                        smtpClient.notifyCloseKon(security=self.security, currentTimeString=nowTimeString)
                        self.rate = self.rate * (1 + round((self.openPrice - self.now_price) / self.now_price, 4)) * (0.9996) * (0.9996)
                        print "$$$$$$$$$$$$Rate:" + str(self.rate)
                        time.sleep(1)
            return

        # mak5 = self.getMAK(matype='5', indexCount=indexCount) * 100
        lemk = self.getLifeEMAK(indexCount=indexCount)
        va = self.getVolumeArrow(indexCount=indexCount)
        edge_va = 7
        # 开多仓
        if self.status.status == 'waiting' and \
                self.now_pricePosi == self.pricePosi_top and \
                self.enableBuy is True:
            # half auto interaction with me
            # -------------------------------------------------------------------------------------
            if indexCount == self.indexList.__len__() - 1:
                smtpClient.notifyOpenDuo(security=self.security, currentTimeString=nowTimeString)
            # -------------------------------------------------------------------------------------
            self.status.lockClose = 0
            self.status.buyStartClose = self.now_price
            self.status.shortStartClose = 0
            self.status.preStatus = self.status.status
            self.status.status = 'holdingbuy'

        # 开空仓
        if self.status.status == 'waiting' and \
                self.now_pricePosi == self.pricePosi_bottom and \
                self.enableShort is True:
            # half auto interaction with me
            # -------------------------------------------------------------------------------------
            if indexCount == self.indexList.__len__() - 1:
                smtpClient.notifyOpenKon(security=self.security, currentTimeString=nowTimeString)
            # -------------------------------------------------------------------------------------
            self.status.lockClose = 0
            self.status.buyStartClose = 0
            self.status.shortStartClose = self.now_price
            self.status.preStatus = self.status.status
            self.status.status = 'holdingshort'

    def getVolumeArrow(self, indexCount):
        if indexCount is None:
            indexList = self.indexList
        else:
            indexList = self.indexList[0:indexCount + 1]
        volumes = []
        for index in indexList:
            v = self.df.loc[index, 'volume']
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
        return count - 1

    def getHighPriceArrow(self, indexCount):
        if indexCount is None:
            indexList = self.indexList
        else:
            indexList = self.indexList[0:indexCount + 1]
        volumes = []
        for index in indexList:
            v = self.df.loc[index, 'high']
            volumes.append(v)
        count = 0
        max = None
        while count < indexList.__len__() - 1:
            v = volumes[indexList.__len__() - count - 1]
            if max is None:
                max = v
            elif v > max:
                return count - 1
            count = count + 1
        return count - 1

    def getLowPriceArrow(self, indexCount):
        if indexCount is None:
            indexList = self.indexList
        else:
            indexList = self.indexList[0:indexCount + 1]
        volumes = []
        for index in indexList:
            v = self.df.loc[index, 'low']
            volumes.append(v)
        count = 0
        max = None
        while count < indexList.__len__() - 1:
            v = volumes[indexList.__len__() - count - 1]
            if max is None:
                max = v
            elif v < max:
                return count - 1
            count = count + 1
        return count - 1

    def getRate(self, preCount=0, indexCount=None, nowTimeString=None):
        if indexCount is not None:
            open = float(self.df.loc[self.indexList[indexCount], 'open'])
            close = float(self.df.loc[self.indexList[indexCount], 'close'])
            rate = round((close - open) / open, 4) * 100
            return rate
        open = float(self.df.loc[self.indexList[-1-preCount], 'open'])
        close = float(self.df.loc[self.indexList[-1-preCount], 'close'])
        rate = round((close-open)/open, 4)*100
        return rate

    def getLifeEMAK(self, preCount=0, indexCount=None):
        if indexCount is not None:
            f = self.getEMAK(ematype='5', indexCount=indexCount)
            t = self.getEMAK(ematype='10', indexCount=indexCount)
            return f + t
        f = self.getEMAK(ematype='5', preCount=preCount)
        t = self.getEMAK(ematype='10', preCount=preCount)
        return f + t

    def getEMADistance(self, ematypes=('5', '10', '20', '40', '60'), preCount=0, indexCount=None):

        if indexCount is not None:
            values = []
            for ematype in ematypes:
                values.append(float(self.df.loc[self.indexList[indexCount], 'EMA' + ematype]))
            preV = None
            firstV = None
            distance = 0
            for value in values:
                if firstV is None:
                    firstV = value
                if preV is not None:
                    distance = distance + abs(value - preV) / ematypes.__len__()
                preV = value
            return round(distance / ematypes.__len__() / firstV, 8) * 100

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
                distance = distance + abs(value - preV) / ematypes.__len__()
            preV = value
        return round(distance / ematypes.__len__() / firstV, 8) * 100

    def getEMAK(self, preCount=0, ematype='5', indexCount=None):

        if indexCount is not None:
            ema_now = float(self.df.loc[self.indexList[indexCount], 'EMA' + ematype])
            if indexCount == 0:
                ema_pre = ema_now
            else:
                ema_pre = float(self.df.loc[self.indexList[indexCount - 1], 'EMA' + ematype])
            banlance = ema_now / 1000
            return (ema_now - ema_pre) / banlance * 3

        ema_1 = float(self.df.loc[self.indexList[-1 - preCount], 'EMA' + ematype])
        a = ema_1 / 1000
        ema_2 = float(self.df.loc[self.indexList[-2 - preCount], 'EMA' + ematype])
        return (ema_1 - ema_2) / a * 3

    def getMAK(self, preCount=0, matype='5', indexCount=None):

        if indexCount is not None:
            ma_now = float(self.df.loc[self.indexList[indexCount], 'MA' + matype])
            if indexCount == 0:
                ma_pre = ma_now
            else:
                ma_pre = float(self.df.loc[self.indexList[indexCount - 1], 'MA' + matype])
            banlance = ma_now / 1000
            return (ma_now - ma_pre) / banlance * 3

        ma_1 = float(self.df.loc[self.indexList[-1 - preCount], 'MA' + matype])
        a = ma_1 / 1000
        ma_2 = float(self.df.loc[self.indexList[-2 - preCount], 'MA' + matype])
        return (ma_1 - ma_2) / a * 3

    def getMAValue(self, matype='5', indexCount=None):
        ma_now = float(self.df.loc[self.indexList[indexCount], 'MA' + matype])
        return ma_now

    def startJudgeAndRefreshStatus(self, currentTimeForTesting=None):

        isAllowStartJudge = msbh.shouldStartJudge(self, currentTimeForTesting)

        if isAllowStartJudge is False:
            return False
        if self.enableTrade is True:
            time.sleep(19)

        jqdatasdk.auth(self.jqDataAccount, self.jqDataPassword)

        nowTimeString = self.getNowTimeString(currentTimeForTesting=currentTimeForTesting)

        self.df = self.getAdvancedData(nowTimeString=nowTimeString)

        self.indexList = self.getIndexList()

        self.pricePositions = self.getPricePosiArray()

        self.refreshStatus(nowTimeString)

        return True

    def buy(self, tick):
        status = self.status.status
        if status == 'holdingbuy' and self.isWait() is True and self.isHoldingBuy() is False:
            if self.enableTrade is True:
                self.ctaTemplate.buy(tick.upperLimit*0.995, int32(self.maxPosition))
                self.controlRisk.releaseAll()
                self.controlRisk.setOpenDuoPrice(tick.lastPrice)

            self.writeCtaLog('开多' + str(self.maxPosition) + '手')
            self.duo_position = self.maxPosition
            self.writeCtaLog('############################################多单持仓：' + str(self.duo_position) + ' 空单持仓：' + str(self.kong_position))
            dao.updatePosition(self.duo_position, self.kong_position, self.security)
            self.traded = True  # 在def trade方法复原为False
            return True
        return False

    def short(self, tick):
        status = self.status.status
        if status == 'holdingshort' and self.isWait() is True and self.isHoldingShort() is False:
            if self.enableTrade is True:
                self.ctaTemplate.short(tick.lowerLimit*1.005, int32(self.maxPosition))
                self.controlRisk.releaseAll()
                self.controlRisk.setOpenKonPrice(tick.lastPrice)

            self.writeCtaLog('开空' + str(self.maxPosition) + '手')
            self.kong_position = self.maxPosition
            self.writeCtaLog('############################################多单持仓：' + str(self.duo_position) + ' 空单持仓：' + str(self.kong_position))
            dao.updatePosition(self.duo_position, self.kong_position, self.security)
            self.traded = True  # 在def trade方法复原为False
            return True
        return False

    def closePosition(self, tick):
        status = self.status.status
        if status == 'waiting' and self.isWait() is False and self.isHoldingBuy() is True:
            if self.enableTrade is True:
                self.ctaTemplate.sell(tick.lowerLimit*1.005, int32(self.maxPosition)) # 平多
                self.controlRisk.releaseAll()

            self.writeCtaLog('平多' + str(self.maxPosition) + '手')
            self.duo_position = 0
            self.writeCtaLog('############################################多单持仓：' + str(self.duo_position) + ' 空单持仓：' + str(self.kong_position))
            dao.updatePosition(self.duo_position, self.kong_position, self.security)
            self.traded = True  # 在def trade方法复原为False

        if status == 'waiting' and self.isWait() is False and self.isHoldingShort() is True:
            if self.enableTrade is True:
                self.ctaTemplate.cover(tick.upperLimit*0.995, int32(self.maxPosition)) # 平空
                self.controlRisk.releaseAll()

            self.writeCtaLog('平空' + str(self.maxPosition) + '手')
            self.kong_position = 0
            self.writeCtaLog('############################################多单持仓：' + str(self.duo_position) + ' 空单持仓：' + str(self.kong_position))
            dao.updatePosition(self.duo_position, self.kong_position, self.security)
            self.traded = True  # 在def trade方法复原为False

        if status == 'waiting' and self.isWait() is False: # 双平
            if self.duo_position > 0 and self.isHoldingBuy():
                if self.enableTrade is True:
                    self.ctaTemplate.sell(tick.lowerLimit*1.005, int32(self.maxPosition))  # 平多
                    self.controlRisk.releaseAll()

                self.writeCtaLog('平多' + str(self.maxPosition) + '手')
            if self.kong_position > 0 and self.isHoldingShort():
                if self.enableTrade is True:
                    self.ctaTemplate.cover(tick.upperLimit*0.995, int32(self.maxPosition))  # 平空
                    self.controlRisk.releaseAll()

                self.writeCtaLog('平空' + str(self.maxPosition) + '手')
            self.duo_position = 0
            self.kong_position = 0
            dao.updatePosition(0, 0, self.security)
            self.traded = True  # 在def trade方法复原为False

    def trade(self, tick):
        self.buy(tick)
        self.short(tick)
        self.closePosition(tick)
        try:
            if self.traded == True:
                time.sleep(3)
                smtpClient.notifyTrade(security=self.security)
                self.traded = False
        except:
            return

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