# encoding: UTF-8

class Status:

    def __init__(self, status='waiting', buyStartClose=0, shortStartClose=0, lockClose=0):
        self.status = status
        self.preStatus = None
        self.buyStartClose = buyStartClose
        self.shortStartClose = shortStartClose
        self.lockClose = lockClose

    def shouldLock(self, lastestPrice):
        if self.status == 'holdingbuy' and self.buyStartClose > lastestPrice:
            return True
        if self.status == 'holdingshort' and self.shortStartClose < lastestPrice:
            return True
        return False

