#: encoding: utf8

import requests
import PyBase.Util as util
import PyBase.Dao as dao

enable = False

def sendEmail(subject, content, receivers='jacklaiu@163.com'):
    print("@@@@@@@@@@@@@->subject: " + subject + " content: " + content)
    if enable is False: return
    url = 'http://107.182.31.161:64210/smtpclient/sendHtml?subject='+subject+'&content='+content+'&receivers='+receivers
    requests.get(url)

def notifyError(content):
    currentTimeString = util.getYMDHMS()
    sendEmail(subject='['+str(currentTimeString)+'] 错误：' + content, content=str(content))

def notifyUnLockKon(security):
    security = util.futureName(security)
    currentTimeString = util.getYMDHMS()
    a = '<a href="http://107.182.31.161:5288/">查看行情</a>'
    sendEmail(subject='['+str(currentTimeString)+'] 解锁空（重新开空仓）_' + security, content='' + a)

def notifyUnLockDuo(security):
    security = util.futureName(security)
    currentTimeString = util.getYMDHMS()
    a = '<a href="http://107.182.31.161:5288/">查看行情</a>'
    sendEmail(subject='['+str(currentTimeString)+'] 解锁多（重新开多仓）_' + security, content='' + a)

def notifyLockKon(security):
    security = util.futureName(security)
    currentTimeString = util.getYMDHMS()
    a = '<a href="http://107.182.31.161:5288/">查看行情</a>'
    sendEmail(subject='['+str(currentTimeString)+'] 锁空（平空仓）_' + security, content='' + a)

def notifyLockDuo(security):
    security = util.futureName(security)
    currentTimeString = util.getYMDHMS()
    a = '<a href="http://107.182.31.161:5288/">查看行情</a>'
    sendEmail(subject='['+str(currentTimeString)+'] 锁多（平多仓）_' + security, content='' + a)

def notifyVolumeUnusual(security, volumeArrowCount=0):
    currentTimeString = util.getYMDHMS()
    content = '<div style="padding: 10px">' \
            '<a href="http://107.182.31.161:5288/candle_sticks?security='+security+'" style="font-weight: bold;">查看走势</a>' \
        '</div>'
    sendEmail(subject='['+str(currentTimeString)+'] 成交量大增:'+str(volumeArrowCount)+'_' + util.futureName(security), content='' + content)

def notifyTrade(security, nowRate="?"):
    currentTimeString = util.getYMDHMS()
    duo = str(int(dao.readDuoPosition(security=security)))
    kon = str(int(dao.readKongPosition(security=security)))
    max = str(int(dao.readMaxPosition(security=security)))
    a = '<p>duo: <strong>'+duo+'</strong></p><p>kon: <strong>'+kon+'</strong></p><p>max: <strong>'+max+'</strong></p>'
    sendEmail(subject='['+str(currentTimeString)+'] 触发交易动作_' + util.futureName(security), content='rate: ' + nowRate + ' duo: ' + duo + ' kon: ' + kon + ' max: ' + max)

def notifyOpenKon(security, currentTimeString=None):
    if currentTimeString is None:
        currentTimeString = util.getYMDHMS()
    a = '<a href="http://107.182.31.161:5288/">查看行情</a>'
    sendEmail(subject='['+str(currentTimeString)+'] Kon开_' + util.futureName(security), content='' + a)

def notifyOpenDuo(security, currentTimeString=None):
    if currentTimeString is None:
        currentTimeString = util.getYMDHMS()
    a = '<a href="http://107.182.31.161:5288/">查看行情</a>'
    sendEmail(subject='['+str(currentTimeString)+'] Duo开_' + util.futureName(security), content='' + a)

def notifyCloseKon(security, currentTimeString=None):
    if currentTimeString is None:
        currentTimeString = util.getYMDHMS()
    a = '<a href="http://107.182.31.161:5288/">查看行情</a>'
    sendEmail(subject='['+str(currentTimeString)+'] Kon平_' + util.futureName(security), content='' + a)

def notifyCloseDuo(security, currentTimeString=None):
    if currentTimeString is None:
        currentTimeString = util.getYMDHMS()
    a = '<a href="http://107.182.31.161:5288/">查看行情</a>'
    sendEmail(subject='['+str(currentTimeString)+'] Duo平_' + util.futureName(security), content='' + a)

