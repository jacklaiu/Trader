# encoding: UTF-8

import time
import Util as util

def isTradingTime(self, currentTimeForTesting):
    if currentTimeForTesting is None:
        now = time.strftime('%H:%M:%S' ,time.localtime(time.time()))
    else:
        ts = util.string2timestamp(currentTimeForTesting)
        now = time.strftime('%H:%M:%S', time.localtime(ts))
    if now >= self.dayStartTime and now <= self.dayEndTime:
        return True
    if now >= self.afternoonStartTime and now <= self.afternoonEndTime:
        return True
    if now >= self.noonStartTime and now <= self.noonEndTime:
        return True
    if self.nightStartTime is not None and now >= self.nightStartTime and now <= self.nightEndTime:
        return True

    return False

def shouldStartJudge(self, currentTimeForTesting=None):
    currentTimestamp = time.time() * 1000
    flag_isTradingTime = isTradingTime(self, currentTimeForTesting)
    if currentTimeForTesting is not None:
        if util.isWeekend(currentTimeForTesting) is True:
            return False
        ts  = util.string2timestamp(currentTimeForTesting)
        frequencyLimitFlag = int(time.strftime('%M', time.localtime(ts))) % int(self.frequency[0:-1]) == 0
        currentTimestamp = util.string2timestamp(currentTimeForTesting) * 1000
    else:
        n = int(time.strftime('%M', time.localtime(currentTimestamp/1000))) % int(self.frequency[0:-1])
        frequencyLimitFlag = n == 0

    if flag_isTradingTime is True and self.lastExeTime is None: # 第一次
        if frequencyLimitFlag is True:
            self.lastExeTime = currentTimestamp
            return True
        else:
            return False
    elif flag_isTradingTime is True and currentTimestamp - self.lastExeTime > 66 * 1000: # 当前时间已经距离上次调用更新状态过了self.waittime分钟，可以再次调用
        if frequencyLimitFlag is True:
            self.lastExeTime = currentTimestamp
            return True
        else:
            return False
    return False

