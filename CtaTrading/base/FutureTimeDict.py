# encoding: UTF-8
MSG = {}
#RB螺纹钢
rbMsg = {}
rbMsg.setdefault('dayStartTime', '09:00:20')
rbMsg.setdefault('dayEndTime', '10:14:00')
rbMsg.setdefault('noonStartTime', '10:30:00')
rbMsg.setdefault('noonEndTime', '11:29:00')
rbMsg.setdefault('afternoonStartTime', '13:30:00')
rbMsg.setdefault('afternoonEndTime', '14:59:00')
rbMsg.setdefault('nightStartTime', '21:00:00')
rbMsg.setdefault('nightEndTime', '22:59:00')
MSG.setdefault('rb', rbMsg)

#JM焦煤
jmMsg = {}
jmMsg.setdefault('dayStartTime', '09:00:20')
jmMsg.setdefault('dayEndTime', '10:14:00')
jmMsg.setdefault('noonStartTime', '10:30:00')
jmMsg.setdefault('noonEndTime', '11:29:00')
jmMsg.setdefault('afternoonStartTime', '13:30:00')
jmMsg.setdefault('afternoonEndTime', '14:59:00')
jmMsg.setdefault('nightStartTime', '21:00:00')
jmMsg.setdefault('nightEndTime', '23:29:00')
MSG.setdefault('jm', jmMsg)

#PTA
taMsg = {}
taMsg.setdefault('dayStartTime', '09:00:20')
taMsg.setdefault('dayEndTime', '10:14:00')
taMsg.setdefault('noonStartTime', '10:30:00')
taMsg.setdefault('noonEndTime', '11:29:00')
taMsg.setdefault('afternoonStartTime', '13:30:00')
taMsg.setdefault('afternoonEndTime', '14:59:00')
taMsg.setdefault('nightStartTime', '21:00:00')
taMsg.setdefault('nightEndTime', '23:29:00')
MSG.setdefault('ta', taMsg)

#M
taMsg = {}
taMsg.setdefault('dayStartTime', '09:00:20')
taMsg.setdefault('dayEndTime', '10:14:00')
taMsg.setdefault('noonStartTime', '10:30:00')
taMsg.setdefault('noonEndTime', '11:29:00')
taMsg.setdefault('afternoonStartTime', '13:30:00')
taMsg.setdefault('afternoonEndTime', '14:59:00')
taMsg.setdefault('nightStartTime', '21:00:00')
taMsg.setdefault('nightEndTime', '23:29:00')
MSG.setdefault('m9', taMsg)

# PP
taMsg = {}
taMsg.setdefault('dayStartTime', '09:00:20')
taMsg.setdefault('dayEndTime', '10:14:00')
taMsg.setdefault('noonStartTime', '10:30:00')
taMsg.setdefault('noonEndTime', '11:29:00')
taMsg.setdefault('afternoonStartTime', '13:30:00')
taMsg.setdefault('afternoonEndTime', '14:59:00')
MSG.setdefault('pp', taMsg)

# MA
taMsg = {}
taMsg.setdefault('dayStartTime', '09:00:20')
taMsg.setdefault('dayEndTime', '10:14:00')
taMsg.setdefault('noonStartTime', '10:30:00')
taMsg.setdefault('noonEndTime', '11:29:00')
taMsg.setdefault('afternoonStartTime', '13:30:00')
taMsg.setdefault('afternoonEndTime', '14:59:00')
taMsg.setdefault('nightStartTime', '21:00:00')
taMsg.setdefault('nightEndTime', '23:29:00')
MSG.setdefault('ma', taMsg)

def getFutureMsg(futureName):
    futureName = futureName[0:2].lower()
    ret = None
    try:
        ret = MSG[futureName]
    except:
        ret = {}
        ret.setdefault('dayStartTime', '09:00:20')
        ret.setdefault('dayEndTime', '10:14:00')
        ret.setdefault('noonStartTime', '10:30:00')
        ret.setdefault('noonEndTime', '11:29:00')
        ret.setdefault('afternoonStartTime', '13:30:00')
        ret.setdefault('afternoonEndTime', '14:59:00')
        ret.setdefault('nightStartTime', '21:00:00')
        ret.setdefault('nightEndTime', '23:29:00')
        return ret
    return ret
