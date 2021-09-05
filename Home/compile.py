import os, re
import time
from urllib.parse import unquote

import requests
from Home.ZipUtilities import ZipUtilities
from FrexTTest.settings import compileZipPath, compileBitPath, compileErrPath, Compile_MAX_Thread, Compile_Time_Unit
from FrexTTest.settings import compileUrl

from threading import Thread, Timer

import logging
logger = logging.getLogger(__name__)



def compileHandle(expFiles, topModuleName):
    if expFiles:
        if not os.path.exists(compileZipPath):
            os.makedirs(compileZipPath)
        if not os.path.exists(compileBitPath):
            os.makedirs(compileBitPath)
        if not os.path.exists(compileErrPath):
            os.makedirs(compileErrPath)

        tempFilePath = compileZipPath + "ljw_test_{0}.zip".format(len(os.listdir(compileZipPath)))
        utilities = ZipUtilities()
        for f in expFiles:
            print(f.file.path)
            utilities.toZip(f.file.path, f.file_name)

        z = utilities.zip_file
        z.write(tempFilePath)
        with open(tempFilePath, 'wb') as f:
            for data in z:
                f.write(data)
        logger.warning("true zip over")

        result = compileBit(tempFilePath, topModuleName)
        return result

    return {'state': "ERROR", 'info': "没有文件可以编译"}


def compileBit(filePath, topModuleName):
    logger.warning(filePath + topModuleName)
    files = {'file': open(filePath, 'rb')}
    params = {'topModuleName': topModuleName}
    req = requests.get(url=compileUrl, files=files, params=params, stream=True)
    logger.warning(req)
    print(req.headers)


    filename = "找不到文件.log"
    disposition_split = req.headers['Content-Disposition'].split(';')
    if disposition_split[1].strip().lower().startswith('filename='):
        file_name = disposition_split[1].split('=')
        if len(file_name) > 1:
            filename = unquote(file_name[1])
            print(filename)

    if req.status_code == 200 and filename.split('.')[1] == "bit":
        # tempFileName = "default_{0}.bit".format(len(os.listdir(compileBitPath)))
        tempFileName = filename
        tempFilePath = compileBitPath
        with open(tempFilePath+tempFileName, "wb") as downfile:
            for chunk in req.iter_content(chunk_size=1024):
                if chunk:
                    downfile.write(chunk)
        return {'state': "OK", 'bitFilePath': tempFilePath, 'bitFileName': tempFileName, 'info': "编译成功"}
    else:
        # tempFileName = "default_{0}.log".format(len(os.listdir(compileErrPath)))
        tempFileName = filename
        tempFilePath = compileErrPath
        with open(tempFilePath+tempFileName, "wb") as downfile:
            for chunk in req.iter_content(chunk_size=1024):
                if chunk:
                    downfile.write(chunk)

        compileInfo = ""
        for line in open(tempFilePath+tempFileName):
            line = line.strip('\n')
            regex = re.compile('^ERROR')
            m = re.match(regex, line)
            if m is not None:
                compileInfo = compileInfo + line + "\n"

        return {'state': "ERROR", 'compileInfo': compileInfo, 'info': "编译失败",
                'logFilePath': tempFilePath, 'logFileName': tempFileName}


class CompileThread(Thread):
    def __init__(self, func, content):
        super(CompileThread, self).__init__()
        self.func = func
        self.content = content

    def run(self):
        self.result = self.func(self.content['tempFilePath'],
                                self.content['topModuleName'])
        if self.result['state'] == "OK":
            self.content['bitFileName'] = self.result['bitFileName']

    def get_result(self):
        try:
            return self.result
        except Exception:
            return None

    def get_content(self, key):
        return self.content[key]

    def get_contents(self):
        return self.content


class TimeCounter():
    def __init__(self):
        super(TimeCounter, self).__init__()
        self.time = 0

    def time_add(self):
        self.time += Compile_Time_Unit
        Timer(Compile_Time_Unit, self.time_add).start()

    def start(self):
        Timer(Compile_Time_Unit, self.time_add).start()

    def get_time(self):
        return self.time

#
# class TimerThread(Thread):
#     def __init__(self, timeout):
#         super(TimerThread, self).__init__()
#         self.timeout = timeout
#
#     def run(self):
#         time.sleep(self.timeout)
#         self.result = 0
#
#     def get_result(self):
#         try:
#             return self.result
#         except Exception:
#             return None


class CompileHandleThread():
    def __init__(self, compileThread, timeCounter):
        self.compilerThread = compileThread
        self.timeCounter = timeCounter

    def get_compile(self):
        return self.compilerThread.get_result()

    def get_time(self):
        return self.timeCounter.get_time()

    def start(self):
        self.compilerThread.start()
        self.timeCounter.start()

    def get_content(self, key):
        return self.compilerThread.get_content(key)

    def get_contents(self):
        return self.compilerThread.get_contents()




def funccc(filePath, topModuleName):
    print(filePath)
    print(topModuleName)
    time.sleep(20)
    return 1,2,3

if __name__ == '__main__':
    # compileBit("/tmp/torn.zip", "topMod60Counter")
    t1 = CompileThread(funccc, "123", "234")
    t2 = CompileThread(funccc, "1234", "2345")
    t3 = CompileThread(funccc, "12345", "23456")
    ljw = {"1": t1, "2": t2, "3": t3}
    t1.start()
    t2.start()
    t3.start()
    for i in range(0, 3):
        time.sleep(7)
        ljw[str(i)].join(1)
        if ljw[str(i)].get_result() == None:
            print("not over")
        else:
            print("over")
            print(ljw[str(i)].get_result())


