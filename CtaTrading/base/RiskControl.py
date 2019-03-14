### coding: utf8
from numpy import int32
import base.SmtpClient as smtp
import base.Util as util
import base.Dao as dao
RiskControlRate = -0.2

class ControlRisk():

    def __init__(self, security, ctaEngine):
        self.security = security
        self.ctaEngine = ctaEngine
        self.lockActionToken = False # 瞬间动作标记
        self.unlockActionToken = False # 瞬间动作标记
        self.maxPosition = dao.readMaxPosition(security=security)
        print "RickControl初始化：已从DB读取maxPosition：" + str(self.maxPosition)
        self.realOpenKonPrice = dao.readRealOpenKonPrice(security=self.security)
        print "RickControl初始化：已从DB读取realOpenKonPrice：" + str(self.realOpenKonPrice)
        self.realOpenDuoPrice = dao.readRealOpenDuoPrice(security=self.security)
        print "RickControl初始化：已从DB读取realOpenDuoPrice：" + str(self.realOpenDuoPrice)
        self.locking = dao.readLocking(security=self.security)
        print "RickControl初始化：已从DB读取locking：" + str(self.locking)

        print('RickControl初始化：完成')

    def activeLocking(self):
        self.locking = True
        dao.activeLocking(security=self.security)

    def setOpenDuoPrice(self, price):
        print '设置realOpenDuoPrice：' + str(price)
        self.realOpenDuoPrice = price
        # 持久化，下次策略重载时风控对象重新初始化从数据库读取
        dao.setRealOpenDuoPrice(security=self.security, price=price)

    def setOpenKonPrice(self, price):
        print '设置realOpenKonPrice：' + str(price)
        self.realOpenKonPrice = price
        # 持久化，下次策略重载时风控对象重新初始化从数据库读取
        dao.setRealOpenKonPrice(security=self.security, price=price)

    def setMaxPosition(self, posi):
        self.maxPosition = posi

    def setSecurity(self, security):
        self.security = security

    def setCtaEngine(self, engine):
        self.ctaEngine = engine

    def releaseAll(self):
        print '清空风控设置'
        self.realOpenKonPrice = None
        self.realOpenDuoPrice = None
        self.locking = False
        # 持久化，下次策略重载时风控对象重新初始化从数据库读取
        dao.releaseRealOpenKonPrice(security=self.security)
        dao.releaseRealOpenDuoPrice(security=self.security)
        dao.releaseLocking(security=self.security)

    def controlOnTick(self, tick):

        if self.realOpenDuoPrice is not None and self.realOpenKonPrice is not None:
            smtp.notifyError('realOpenDuoPrice和realOpenKonPrice都不为空，将中止进程')
            exit()

        # 监听区域!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!##########################################
        # 持有多仓风控计算实时盈亏
        rate = None
        if self.realOpenKonPrice is not None:
            openPrice = self.realOpenKonPrice
            rate = round((openPrice - tick.lastPrice) / openPrice, 8) * 100
            print '[' + str(util.getYMDHMS()) + '] RiskControl realOpenKonPrice: ' + str(self.realOpenDuoPrice) + ' rate: ' + str(rate)
            if rate < RiskControlRate:
                self.lockActionToken = True # 发出放狗指令
            if self.locking is True and rate > -RiskControlRate:
                self.unlockActionToken = True # 发出放狗指令

        # 持有空仓风控计算实时盈亏
        elif self.realOpenDuoPrice is not None:
            openPrice = self.realOpenDuoPrice
            rate = round((tick.lastPrice - openPrice) / openPrice, 8) * 100
            print '[' + str(util.getYMDHMS()) + '] RiskControl realOpenDuoPrice: ' + str(self.realOpenDuoPrice) + ' rate: ' + str(rate)
            if rate < RiskControlRate:
                self.lockActionToken = True# 发出放狗指令
            if self.locking is True and rate > -RiskControlRate:
                self.unlockActionToken = True# 发出放狗指令


        #Return的话，说明还没有开仓，或者开仓时候没有设置这两个值
        if self.realOpenDuoPrice is None and self.realOpenKonPrice is None:
            return

        # 动作执行区域!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!##########################################
        # 锁动作执行
        if self.lockActionToken is True and self.locking is False:
            if self.realOpenKonPrice is not None:
                if self.ctaEngine is not None:
                    self.ctaEngine.cover(tick.upperLimit * 0.995, int32(self.maxPosition))  # 平空!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                    smtp.notifyLockKon(security=self.security)

            if self.realOpenDuoPrice is not None:
                if self.ctaEngine is not None:
                    self.ctaEngine.sell(tick.lowerLimit * 1.005, int32(self.maxPosition))  # 平多!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                    smtp.notifyLockDuo(security=self.security)

            self.locking = True
            # 持久化，下次策略重载时风控对象重新初始化从数据库读取
            dao.activeLocking(security=self.security)
            self.lockActionToken = False

        # 解锁动作执行
        if self.unlockActionToken is True and self.locking is True:
            if self.realOpenKonPrice is not None:
                if self.ctaEngine is not None:
                    smtp.notifyUnLockKon(security=self.security)

            if self.realOpenDuoPrice is not None:
                if self.ctaEngine is not None:
                    smtp.notifyUnLockDuo(security=self.security)

            self.locking = False
            # 持久化，下次策略重载时风控对象重新初始化从数据库读取
            dao.releaseLocking(security=self.security)
            self.unlockActionToken = False
