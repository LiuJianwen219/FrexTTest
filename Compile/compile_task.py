from threading import Thread, Timer

import logging
from Compile.RabbitMQClient import CompileRabbitMQHandler
logger = logging.getLogger(__name__)


class CompileTaskThread(Thread):
    def __init__(self, func, content):
        super(CompileTaskThread, self).__init__()
        self.func = func
        self.content = content
        self.result = None

    def run(self):
        self.result = self.func(self.content)
        if self.result and self.result['state'] == "OK":
            print("compile thread response ", self.result)

    def get_result(self):
        try:
            return self.result
        except ConnectionError:
            return None

    def get_content(self, key):
        return self.content[key]

    def get_contents(self):
        return self.content


def send_task_to_rabbit_mq(content):
    logger.info(content)
    rabbitMQ = CompileRabbitMQHandler()
    result = rabbitMQ.call(content)
    return result
# example result
# data = {'state': "OK", 'message': r.json()['message'], 'content': content}
