from threading import Thread, Timer

from Home.RocketMQHandler import RabbitMQHandler
from FrexTTest.settings import Judge_Time_Unit


def exection(content):
    rabbitMQ = RabbitMQHandler()
    result = rabbitMQ.call(content)
    return result[0], result[1], result[2]


class JudgeThread(Thread):
    def __init__(self, func, content):
        super(JudgeThread, self).__init__()
        self.func = func
        self.content = content

    def run(self):
        self.result = self.func(self.content)

    def get_result(self):
        try:
            return self.result
        except Exception:
            return None

    def get_content(self, key):
        return self.content[key]

    def get_contents(self):
        return self.content


class JudgeTimeCounter():
    def __init__(self):
        super(JudgeTimeCounter, self).__init__()
        self.time = 0

    def time_add(self):
        self.time += Judge_Time_Unit
        Timer(Judge_Time_Unit, self.time_add).start()

    def start(self):
        Timer(Judge_Time_Unit, self.time_add).start()

    def get_time(self):
        return self.time

class JudgeHandleThread():
    def __init__(self, judgeThread, timeCounter):
        self.judgeThread = judgeThread
        self.timeCounter = timeCounter

    def get_judge(self):
        return self.judgeThread.get_result()

    def get_time(self):
        return self.timeCounter.get_time()

    def start(self):
        self.judgeThread.start()
        self.timeCounter.start()

    def get_content(self, key):
        return self.judgeThread.get_content(key)

    def get_contents(self):
        return self.judgeThread.get_contents()