
import Util as u

def addAskingItem(security, nowTimeString, frequency, action):
    asking_data = u.getProperty('asking_data')
    if asking_data is None:
        asking_data = {}
    if asking_data.get(security) is not None:
        del asking_data[security]
    asking_data.setdefault(security, {'security': security, 'nowTimeString': nowTimeString, 'frequency': frequency, 'ispermit': '-1', 'action': action})
    u.setProperty('asking_data', asking_data)

def getAskingData():
    asking_data = u.getProperty('asking_data')
    return asking_data

def delAskingItem(security):
    asking_data = u.getProperty('asking_data')
    if asking_data.get(security) is not None:
        del asking_data[security]
    u.setProperty('asking_data', asking_data)

def isPermit(security):
    asking_data = u.getProperty('asking_data')
    item = asking_data.get(security)
    if item is None:
        return None
    else:
        ispermit = item.get('ispermit')
        if ispermit == '1':
            return True
        else:
            return False

def isWaiting(security):
    asking_data = u.getProperty('asking_data')
    item = asking_data.get(security)
    if item is None:
        return None
    else:
        ispermit = item.get('ispermit')
        if ispermit == '-1':
            return True
        else:
            return False

def permit(security):
    asking_data = u.getProperty('asking_data')
    item = asking_data.get(security)
    if item is None:
        return None
    else:
        del item['ispermit']
        item.setdefault('ispermit', '1')
        asking_data.setdefault(security, item)
        u.setProperty('asking_data', asking_data)

def deny(security):
    asking_data = u.getProperty('asking_data')
    item = asking_data.get(security)
    if item is None:
        return None
    else:
        del item['ispermit']
        item.setdefault('ispermit', '0')
        asking_data.setdefault(security, item)
        u.setProperty('asking_data', asking_data)


