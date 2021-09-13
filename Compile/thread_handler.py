
from threading import Thread, Timer
from FrexTTest.settings import Compile_Time_Unit
import logging

logger = logging.getLogger(__name__)


class TaskHandlerThread:
    def __init__(self, task_thread, time_counter):
        self.task_thread = task_thread
        self.time_counter = time_counter

    def start(self):
        self.task_thread.start()
        self.time_counter.start()

    def get_task_result(self):
        return self.task_thread.get_result()

    def get_time(self):
        return self.time_counter.get_time()

    def get_content(self, key):
        return self.task_thread.get_content(key)

    def get_contents(self):
        return self.task_thread.get_contents()


class TimeCounter:
    def __init__(self, timeout):
        super(TimeCounter, self).__init__()
        self.time = 0
        self.timeout = timeout

    def time_add(self):
        self.time += Compile_Time_Unit
        Timer(Compile_Time_Unit, self.time_add).start()

    def start(self):
        Timer(Compile_Time_Unit, self.time_add).start()

    def get_time(self):
        return self.time

