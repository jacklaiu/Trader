# encoding: UTF-8
import json
import base.Dao as dao
import base.Util as util
import base.SmtpClient as smtp
from base.RiskControl import ControlRisk

strategy = 'MutilEMaStrategy'

# 下面的合约，受外盘影响小，开盘几乎不怎么跳空，所以选为操作合约
#JM9999.XDCE 【焦煤】
#RB9999.XSGE  【螺纹钢】
#HC9999.XSGE 【热轧卷】
#A9999.XDCE 【豆一】
#CF9999.XZCE 【郑州棉花】

jqdata_security = 'RB9999.XSGE'
frequency = '5m'
duo = 0
kon = 0
max = 1
enableTrade = True
enableBuy = True
enableShort = True
smtp.enable = True

init_realOpenKonPrice = None
init_realOpenDuoPrice = None

riskControlRate = -0.2

def init():
    #（1） 更新t_position，没有就插入
    dao.updateAllPosition(duo=duo, kon=kon, max=max, security=jqdata_security)
    #（2） 更新CTA_setting.json
    vtSymbol = util.get_CTA_setting_dominant_future(jqSecurity=jqdata_security)
    #（3）riskcontrol重设
    controlRisk = ControlRisk(security=jqdata_security, ctaEngine=None)
    controlRisk.releaseAll()
    controlRisk.setOpenKonPrice(price=init_realOpenKonPrice)
    controlRisk.setOpenDuoPrice(price=init_realOpenDuoPrice)
    if init_realOpenDuoPrice is not None or init_realOpenKonPrice is not None:
        controlRisk.activeLocking()
    with open('CTA_setting.json', 'w') as json_file:
        json_file.write(json.dumps(
            [
                {
                    "name": strategy,
                    "className": strategy,
                    "vtSymbol": vtSymbol
                }
            ]
        ))
        print "################# My t_position and CTA_setting.json REFRESH! ######################"