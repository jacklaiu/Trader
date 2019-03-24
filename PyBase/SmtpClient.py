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

