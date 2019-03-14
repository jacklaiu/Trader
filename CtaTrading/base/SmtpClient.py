#: encoding: utf8

import requests
import base.Util as util
import base.Dao as dao

enable = False

def sendEmail(subject, content, receivers='jacklaiu@qq.com'):
    print("@@@@@@@@@@@@@->subject: " + subject + " content: " + content)
    if enable is False: return
    url = 'http://107.182.31.161:64210/smtpclient/sendHtml?subject='+subject+'&content='+subject+'&receivers='+receivers
    requests.get(url)

def notifyError(content):
    currentTimeString = util.getYMDHMS()
    sendEmail(subject='['+str(currentTimeString)+'] 错误：' + content, content=str(content))

def notifyUnLockKon(security):
    currentTimeString = util.getYMDHMS()
    a = '<a href="http://107.182.31.161:5288/">查看行情</a>'
    sendEmail(subject='['+str(currentTimeString)+'] 解锁空（重新开空仓）_' + security, content='' + a)

def notifyUnLockDuo(security):
    currentTimeString = util.getYMDHMS()
    a = '<a href="http://107.182.31.161:5288/">查看行情</a>'
    sendEmail(subject='['+str(currentTimeString)+'] 解锁多（重新开多仓）_' + security, content='' + a)

def notifyLockKon(security):
    currentTimeString = util.getYMDHMS()
    a = '<a href="http://107.182.31.161:5288/">查看行情</a>'
    sendEmail(subject='['+str(currentTimeString)+'] 锁空（平空仓）_' + security, content='' + a)

def notifyLockDuo(security):
    currentTimeString = util.getYMDHMS()
    a = '<a href="http://107.182.31.161:5288/">查看行情</a>'
    sendEmail(subject='['+str(currentTimeString)+'] 锁多（平多仓）_' + security, content='' + a)

def notifyVolumeUnusual(security):
    currentTimeString = util.getYMDHMS()
    a = '<a href="http://107.182.31.161:5288/">查看行情</a>'
    sendEmail(subject='['+str(currentTimeString)+'] 瞬间成交量大增_' + security, content='' + a)

def notifyTrade(security):
    currentTimeString = util.getYMDHMS()
    duo = str(int(dao.readDuoPosition(security=security)))
    kon = str(int(dao.readKongPosition(security=security)))
    max = str(int(dao.readMaxPosition(security=security)))
    a = '<p>duo: <strong>'+duo+'</strong></p><p>kon: <strong>'+kon+'</strong></p><p>max: <strong>'+max+'</strong></p>'
    sendEmail(subject='['+str(currentTimeString)+'] 触发交易动作_' + security, content='' + a)

def notifyOpenKon(security, currentTimeString=None):
    if currentTimeString is None:
        currentTimeString = util.getYMDHMS()
    a = '<a href="http://107.182.31.161:5288/">查看行情</a>'
    sendEmail(subject='['+str(currentTimeString)+'] Kon开_' + security, content='' + a)

def notifyOpenDuo(security, currentTimeString=None):
    if currentTimeString is None:
        currentTimeString = util.getYMDHMS()
    a = '<a href="http://107.182.31.161:5288/">查看行情</a>'
    sendEmail(subject='['+str(currentTimeString)+'] Duo开_' + security, content='' + a)

def notifyCloseKon(security, currentTimeString=None):
    if currentTimeString is None:
        currentTimeString = util.getYMDHMS()
    a = '<a href="http://107.182.31.161:5288/">查看行情</a>'
    sendEmail(subject='['+str(currentTimeString)+'] Kon平_' + security, content='' + a)

def notifyCloseDuo(security, currentTimeString=None):
    if currentTimeString is None:
        currentTimeString = util.getYMDHMS()
    a = '<a href="http://107.182.31.161:5288/">查看行情</a>'
    sendEmail(subject='['+str(currentTimeString)+'] Duo平_' + security, content='' + a)

