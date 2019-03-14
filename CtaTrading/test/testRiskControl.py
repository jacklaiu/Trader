# encoding: UTF-8
import datetime
from base.MutilEMaStrategyBase import MutilEMaStrategyBase
from base.Status import Status
import base.Util as util
import base.Dao as dao

def start(startTime=None, jqSecurity=None, frequency=None, enableBuy=None, enableShort=None):
    security = jqSecurity #'FG9999.XZCE' 'RB9999.XSGE' 'JM9999.XDCE'
    status = Status()
    frequency = frequency
    strategyBase = MutilEMaStrategyBase(security=security,
                                        status=status,
                                        ctaTemplate=None,
                                        frequency=frequency,
                                        jqDataAccount='13268108673',
                                        jqDataPassword='king20110713',
                                        pricePosi_top=0,
                                        pricePosi_bottom=4,
                                        enableTrade=False,
                                        enableBuy=enableBuy,
                                        enableShort=enableShort
                                        )
    times = util.getTimeSerial(startTime, count=1000*800, periodSec=12)
    for t in times:
        if strategyBase.startJudgeAndRefreshStatus(t):
            strategyBase.trade(None)

jqSecurity='RB9999.XSGE'
dao.updateAllPosition(duo=0, kon=0, max=1, security=jqSecurity)
start(jqSecurity=jqSecurity, startTime='2018-12-12 13:45:00', frequency='5m', enableBuy=True, enableShort=True)