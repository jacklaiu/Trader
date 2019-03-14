# encoding: UTF-8

"""
这里的Demo是一个最简单的双均线策略实现
"""

from __future__ import division
from vnpy.trader.app.ctaStrategy.ctaTemplate import (CtaTemplate,
                                                     BarGenerator,
                                                     ArrayManager)
from base.Status import Status
from base.MutilEMaStrategyBase import MutilEMaStrategyBase
import _1_MyTradingMsg as mtm

########################################################################
class MutilEMaStrategy(CtaTemplate):
    """双指数均线策略Demo"""
    className = 'MutilEMaStrategy'
    author = u'jacklaiu@qq.com'
    # 策略参数
    fastWindow = 5  # 快速均线参数
    slowWindow = 10  # 慢速均线参数
    initDays = 30  # 初始化数据所用的天数
    # 策略变量
    fastMa0 = None  # 当前最新的快速EMA
    fastMa1 = None  # 上一根的快速EMA
    slowMa0 = None
    slowMa1 = None
    # 参数列表，保存了参数的名称
    paramList = ['name','className','author','vtSymbol','fastWindow','slowWindow']
    # 变量列表，保存了变量的名称
    varList = ['inited','trading','pos','fastMa0','fastMa1','slowMa0','slowMa1']
    # 同步列表，保存了需要保存到数据库的变量名称
    syncList = ['pos']
    # ----------------------------------------------------------------------
    def __init__(self, ctaEngine, setting):

        super(MutilEMaStrategy, self).__init__(ctaEngine, setting)

        self.bg = BarGenerator(self.onBar)
        self.am = ArrayManager()

        self.frequency = mtm.frequency
        self.pricePosi_top = 0
        self.pricePosi_bot = 4
        self.status = Status()
        self.tick = None
        self.strategyBase = MutilEMaStrategyBase(security=mtm.jqdata_security,
                                                 status=self.status,
                                                 frequency=mtm.frequency,
                                                 ctaTemplate=self,
                                                 enableTrade=mtm.enableTrade,
                                                 enableBuy=mtm.enableBuy,
                                                 enableShort=mtm.enableShort
                                                 )
    # ----------------------------------------------------------------------
    def onInit(self):
        """初始化策略（必须由用户继承实现）"""
        self.writeCtaLog(u'多重EMA策略初始化')
        self.putEvent()

    # ----------------------------------------------------------------------
    def onStart(self):
        """启动策略（必须由用户继承实现）"""
        self.writeCtaLog(u'多重EMA策略启动')
        self.putEvent()

    # ----------------------------------------------------------------------
    def onStop(self):
        """停止策略（必须由用户继承实现）"""
        self.writeCtaLog(u'多重EMA策略停止')
        self.putEvent()

    # ----------------------------------------------------------------------
    def onTick(self, tick):
        """收到行情TICK推送（必须由用户继承实现）"""
        self.bg.updateTick(tick)
        self.tick = tick
        if self.strategyBase.startJudgeAndRefreshStatus():
            self.strategyBase.trade(tick)
            self.putEvent()

    # ----------------------------------------------------------------------
    def onBar(self, bar):
        """收到Bar推送（必须由用户继承实现）"""
        # 发出状态更新事件
        self.putEvent()

    # ----------------------------------------------------------------------
    def onOrder(self, order):
        """收到委托变化推送（必须由用户继承实现）"""
        # 对于无需做细粒度委托控制的策略，可以忽略onOrder
        pass

    # ----------------------------------------------------------------------
    def onTrade(self, trade):
        """收到成交推送（必须由用户继承实现）"""
        # 对于无需做细粒度委托控制的策略，可以忽略onOrder
        pass

    # ----------------------------------------------------------------------
    def onStopOrder(self, so):
        """停止单推送"""
        pass
