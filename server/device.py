import time
from constant import *

class Device:

    def __init__(self, id):
        self.id = id
        self.syncTime = time.time()
        self.state = -1
        self.client = None
        # self.user = None

    def getId(self):
        return self.id

    def readState(self):
        curTime = time.time()
        if self.syncTime + SYS_DELAY > curTime:
            return self.state
        # print(self.syncTime)
        # print(curTime)
        return -1

    def writeState(self, s, t):
        # print(self.syncTime)
        # print(t)
        if self.syncTime <= t:
            self.syncTime = t
            self.state = s
            # print("修改" + str(s))

    def setClient(self, c, t):
        if self.syncTime <= t:
            self.syncTime = t
            self.client = c

    # def setUser(self, u, t):
    #     if self.syncTime < t:
    #         self.syncTime = t
    #         self.user = u

    def getClient(self):
        curTime = time.time()
        if self.syncTime <= curTime:
            return self.client

    # def getUser(self):
    #     curTime = time.time()
    #     if self.syncTime < curTime:
    #         return self.user

    def getTime(self):
        return self.syncTime


    def toDict(self):
        return {
            'id': self.id,
            'syncTime': self.syncTime,
            'state': self.state,
            'client': self.client,
            # 'user': self.user
        }


