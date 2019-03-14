# encoding: UTF-8
import pymysql.cursors
from numpy import int32

host='212.64.7.83'
user='jacklaiu'
password='queue11235813'
db='trading'
charset='utf8mb4'
cursorclass=pymysql.cursors.DictCursor

# host='localhost'
# user='root'
# password='123456'
# db='conceptlistener'
# charset='utf8mb4'
# cursorclass=pymysql.cursors.DictCursor

def getConn():
    connection = pymysql.connect(host=host,
                                 user=user,
                                 password=password,
                                 db=db,
                                 charset=charset,
                                 cursorclass=cursorclass)
    return connection

def updatemany(sql, arr_values):
    connection = getConn()
    try:
        with connection.cursor() as cursor:
            cursor.executemany(sql, arr_values)
        connection.commit()
    except Exception as e:
        connection.rollback()
    finally:
        connection.close()

def update(sql, values):
    connection = getConn()
    try:
        with connection.cursor() as cursor:
            cursor.execute(sql, values)
        connection.commit()
    except Exception as e:
        connection.rollback()
    finally:
        connection.close()

def select(sql, values):
    connection = getConn()
    try:
        with connection.cursor() as cursor:
            cursor.execute(sql, values)
            result = cursor.fetchall()
            return result
    finally:
        connection.close()

# t_position #####################################################################################################

# 如果要重新开始，就在数据库把这个值置0
def readDuoPosition(security):
    if security is None:
        return
    if security.find('.') != -1:
        security = security[0:security.find('.')].lower()
    if select("select count(*) as count from t_position where security=%s", (security))[0]['count'] == 0:
        print u'数据库中找不到security对应的记录'
        exit()
    return float(select('select duo_position from t_position where security=%s', (security))[0]['duo_position'])

# 如果要重新开始，就在数据库把这个值置0
def readKongPosition(security):
    if security is None:
        return
    if security.find('.') != -1:
        security = security[0:security.find('.')].lower()
    if select("select count(*) as count from t_position where security=%s", (security))[0]['count'] == 0:
        print u'数据库中找不到security对应的记录'
        exit()
    return float(select('select kong_position from t_position where security=%s', (security))[0]['kong_position'])

# 这个值只会在数据库改
def readMaxPosition(security):
    if security is None:
        return
    if security.find('.') != -1:
        security = security[0:security.find('.')].lower()
    if select("select count(*) as count from t_position where security=%s", (security))[0]['count'] == 0:
        print u'数据库中找不到security对应的记录'
        exit()
    return float(select('select max_position from t_position where security=%s', (security))[0]['max_position'])

def updatePosition(duo_position, kong_position, security):
    if security.find('.') != -1:
        security = security[0:security.find('.')].lower()
    duo_position = str(duo_position)
    kong_position = str(kong_position)
    if select("select count(*) as count from t_position where security=%s", (security))[0]['count'] == 0:
        print u'数据库中找不到security对应的记录'
        exit()
    update('update t_position set duo_position=%s, kong_position=%s where security=%s',
           (duo_position, kong_position, security))

def updateAllPosition(duo=0, kon=0, max=1, security=None):
    if security.find('.') != -1:
        security = security[0:security.find('.')].lower()
    max_position = str(max)
    duo_position = str(duo)
    kon_position = str(kon)
    if select("select count(*) as count from t_position where security=%s", (security))[0]['count'] == 0:
        update('insert t_position(duo_position, kong_position, max_position, security) values(%s,%s,%s,%s)',
               (duo_position, kon_position, max_position, security))
        return
    update('delete from t_position where security = %s', (security))
    update('insert t_position(duo_position, kong_position, max_position, security) values(%s,%s,%s,%s)',
           (duo_position, kon_position, max_position, security))

# END t_position #####################################################################################################

# t_riskcontrol
def _prepareSecurityName(security):
    if security is None:
        return None
    if security.find('.') != -1:
        return security[0:security.find('.')].lower()
    else:
        return security

def _checkRiskControlRecordFalse2Exit(security):
    security = _prepareSecurityName(security=security)
    if security is None: return
    isExist = select("select count(*) as count from t_riskcontrol where security=%s", (security))[0]['count'] > 0
    if isExist is False:
        update('insert into t_riskcontrol(security) values(%s)', (security))
    return isExist

#realOpenKonPrice---------------------------------------------------------------
def readRealOpenKonPrice(security):
    security = _prepareSecurityName(security=security)
    if security is None: return
    _checkRiskControlRecordFalse2Exit(security=security)
    ret = select('select realOpenKonPrice from t_riskcontrol where security=%s', (security))[0]['realOpenKonPrice']
    if ret is not None:
        return float(ret)
    else:
        return None

def setRealOpenKonPrice(security, price):
    security = _prepareSecurityName(security=security)
    if security is None: return
    _checkRiskControlRecordFalse2Exit(security=security)
    update('update t_riskcontrol set realOpenKonPrice = %s where security = %s', (price, security))

def releaseRealOpenKonPrice(security):
    security = _prepareSecurityName(security=security)
    if security is None: return
    _checkRiskControlRecordFalse2Exit(security=security)
    update('update t_riskcontrol set realOpenKonPrice = %s where security = %s', (None, security))

# setRealOpenKonPrice(security='rb9999', price='2345')
# print readRealOpenKonPrice(security='rb9999')
# releaseRealOpenKonPrice(security='rb9999')
# print readRealOpenKonPrice(security='rb9999')

#realOpenDuoPrice-----------------------------------------------------------------
def readRealOpenDuoPrice(security):
    security = _prepareSecurityName(security=security)
    if security is None: return
    _checkRiskControlRecordFalse2Exit(security=security)
    ret = select('select realOpenDuoPrice from t_riskcontrol where security=%s', (security))[0]['realOpenDuoPrice']
    if ret is not None:
        return float(ret)
    else:
        return None

def setRealOpenDuoPrice(security, price):
    security = _prepareSecurityName(security=security)
    if security is None: return
    _checkRiskControlRecordFalse2Exit(security=security)
    update('update t_riskcontrol set realOpenDuoPrice = %s where security = %s', (price, security))

def releaseRealOpenDuoPrice(security):
    security = _prepareSecurityName(security=security)
    if security is None: return
    _checkRiskControlRecordFalse2Exit(security=security)
    update('update t_riskcontrol set realOpenDuoPrice = %s where security = %s', (None, security))

# setRealOpenDuoPrice(security='rb9999', price='2345')
# print readRealOpenDuoPrice(security='rb9999')
# releaseRealOpenDuoPrice(security='rb9999')
# print readRealOpenDuoPrice(security='rb9999')

#UnLockActionToken--------------------------------------------------------------------------------------
def readLockActionToken(security):
    security = _prepareSecurityName(security=security)
    if security is None: return
    _checkRiskControlRecordFalse2Exit(security=security)
    ret = select('select lockActionToken from t_riskcontrol where security=%s', (security))[0]['lockActionToken']
    if ret is not None:
        if ret == 1:
            return True
        else:
            return False
    else:
        return False

def releaseLockActionToken(security):
    security = _prepareSecurityName(security=security)
    if security is None: return
    _checkRiskControlRecordFalse2Exit(security=security)
    update('update t_riskcontrol set lockActionToken = %s where security = %s', (None, security))

def activeLockActionToken(security):
    security = _prepareSecurityName(security=security)
    if security is None: return
    _checkRiskControlRecordFalse2Exit(security=security)
    update('update t_riskcontrol set lockActionToken = %s where security = %s', (1, security))

# activeLockActionToken(security='rb9999')
# print readLockActionToken(security='rb9999')
# releaseLockActionToken(security='rb9999')
# print readLockActionToken(security='rb9999')

#unlockActionToken--------------------------------------------------------------------------------------
def readUnLockActionToken(security):
    security = _prepareSecurityName(security=security)
    if security is None: return
    _checkRiskControlRecordFalse2Exit(security=security)
    ret = select('select unlockActionToken from t_riskcontrol where security=%s', (security))[0]['unlockActionToken']
    if ret is not None:
        if ret == 1:
            return True
        else:
            return False
    else:
        return False

def releaseUnLockActionToken(security):
    security = _prepareSecurityName(security=security)
    if security is None: return
    _checkRiskControlRecordFalse2Exit(security=security)
    update('update t_riskcontrol set unlockActionToken = %s where security = %s', (None, security))

def activeUnLockActionToken(security):
    security = _prepareSecurityName(security=security)
    if security is None: return
    _checkRiskControlRecordFalse2Exit(security=security)
    update('update t_riskcontrol set unlockActionToken = %s where security = %s', (1, security))

# activeUnLockActionToken(security='rb9999')
# print readUnLockActionToken(security='rb9999')
# releaseUnLockActionToken(security='rb9999')
# print readUnLockActionToken(security='rb9999')

#locking--------------------------------------------------------------------------------------
def readLocking(security):
    security = _prepareSecurityName(security=security)
    if security is None: return
    _checkRiskControlRecordFalse2Exit(security=security)
    ret = select('select locking from t_riskcontrol where security=%s', (security))[0]['locking']
    if ret is not None:
        if ret == 1:
            return True
        else:
            return False
    else:
        return False

def releaseLocking(security):
    security = _prepareSecurityName(security=security)
    if security is None: return
    _checkRiskControlRecordFalse2Exit(security=security)
    update('update t_riskcontrol set locking = %s where security = %s', (None, security))

def activeLocking(security):
    security = _prepareSecurityName(security=security)
    if security is None: return
    _checkRiskControlRecordFalse2Exit(security=security)
    update('update t_riskcontrol set locking = %s where security = %s', (1, security))

# activeLocking(security='rb9999')
# print readLocking(security='rb9999')
# releaseLocking(security='rb9999')
# print readLocking(security='rb9999')

def resetRiskControl(security):
    update('delete from t_riskcontrol where security = %s', (security))
    update('insert into t_riskcontrol(security) values(%s)', (security))