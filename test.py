import datetime
import json
import logging
import os
import threading
import time
import _thread

import requests
from Constant import constants as const
logger = logging.getLogger(__name__)

lock = threading.Lock()

t = 0
a = [0,1,1,0,0]

def printMY(na):
    lock.acquire()
    n = 0
    for i in a:
        if i:
            n += 1
    print("ljw: " + str(n))

    # time.sleep(1)
    lock.release()

if __name__ == "__main__":
    # time_start = time.time()
    # _thread.start_new_thread(printMY, ("Thread-1",))
    # _thread.start_new_thread(printMY, ("Thread-2",))
    # time.sleep(3)
    # time_end = time.time()
    # print('time cost', time_end - time_start, 's')
    print(time.time())
    print(time.asctime(time.localtime(time.time())))

    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    print(time.localtime(time.time()))
    a = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    time.sleep(1)
    b = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
    print(a)
    print(b)
    print(a < b)
    print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'))
    print((datetime.datetime.now()-datetime.timedelta(minutes=1)).strftime('%Y-%m-%d %H:%M:%S.%f'))
