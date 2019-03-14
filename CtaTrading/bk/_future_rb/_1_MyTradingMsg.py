# encoding: UTF-8
import json
import base.Dao as dao
import jqdatasdk
import base.Util as util
#上期所
#
# 代码	名称	代码	名称
# AG9999.XSGE	白银主力合约	PB9999.XSGE	铅主力合约
# AU9999.XSGE	黄金主力合约	RB9999.XSGE	螺纹钢主力合约
# AL9999.XSGE	铝主力合约	RU9999.XSGE	天然橡胶主力合约
# BU9999.XSGE	沥青主力合约	SN9999.XSGE	锡主力合约
# CU9999.XSGE	铜主力合约	WR9999.XSGE	线材主力合约
# FU9999.XSGE	燃油主力合约	ZN9999.XSGE	锌主力合约
# HC9999.XSGE	热卷主力合约	NI9999.XSGE	镍主力合约
# 郑商所
#
# 代码	名称	代码	名称
# CY9999.XZCE	棉纱主力合约	RM9999.XZCE	菜籽粕主力合约
# CF9999.XZCE	棉花主力合约	RM9999.XZCE	菜籽粕主力合约
# FG9999.XZCE	玻璃主力合约	RS9999.XZCE	油菜籽主力合约
# JR9999.XZCE	粳谷主力合约	SF9999.XZCE	硅铁主力合约
# LR9999.XZCE	晚稻主力合约	SM9999.XZCE	锰硅主力合约
# MA9999.XZCE	甲醇主力合约	SR9999.XZCE	白糖主力合约
# TA9999.XZCE	PTA主力合约
# OI9999.XZCE	菜油主力合约
# PM9999.XZCE	普麦主力合约	ZC9999.XZCE	动力煤主力合约
# AP9999.XZCE	苹果主力合约
# 大商所
#
# 代码	名称	代码	名称
# A9999.XDCE	豆一主力合约	JD9999.XDCE	鸡蛋主力合约
# B9999.XDCE	豆二主力合约	JM9999.XDCE	焦煤主力合约
# BB9999.XDCE	胶板主力合约	L9999.XDCE	聚乙烯主力合约
# C9999.XDCE	玉米主力合约	M9999.XDCE	豆粕主力合约
# CS9999.XDCE	淀粉主力合约	P9999.XDCE	棕榈油主力合约
# FB9999.XDCE	纤板主力合约	PP9999.XDCE	聚丙烯主力合约
# I9999.XDCE	铁矿主力合约	V9999.XDCE	聚氯乙烯主力合约
# J9999.XDCE	焦炭主力合约	Y9999.XDCE	豆油主力合约

jqdata_security = 'RB9999.XDCE'
frequency = '10m'
max = 1
strategy = 'MutilEMaStrategy'

enableTrade = False
enableBuy = True
enableShort = True

def init():
    #（1） 更新t_position，没有就插入
    dao.updateAllPosition(max, jqdata_security)
    #（2） 更新CTA_setting.json
    with open('CTA_setting.json', 'w') as json_file:
        json_file.write(json.dumps(
            [
                {
                    "name": strategy,
                    "className": strategy,
                    "vtSymbol": util.get_CTA_setting_dominant_future(jqSecurity=jqdata_security)
                }
            ]
        ))
        print "################# My t_position and CTA_setting.json REFRESH! ######################"