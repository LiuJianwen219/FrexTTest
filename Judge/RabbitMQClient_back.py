import uuid
import pika
import json
from FrexTTest.settings import Rabbit_MQ_IP, Rabbit_MQ_QueueID_Judge
from FrexTTest.settings import Rabbit_MQ_USER, Rabbit_MQ_PASS, Rabbit_MQ_Port, Rabbit_MQ_VHOST
import logging

logger = logging.getLogger(__name__)


class JudgeRabbitMQHandler:
    def __init__(self):
        self.auth = pika.PlainCredentials(Rabbit_MQ_USER, Rabbit_MQ_PASS)
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=Rabbit_MQ_IP, port=Rabbit_MQ_Port,
                                      virtual_host=Rabbit_MQ_VHOST, credentials=self.auth,
                                      heartbeat_interval=0))  # heartbeat?
        self.channel = self.connection.channel()
        self.response = None
        self.correlation_id = None
        # 定义一个队列，随机取名，但是当本进程结束后自动销毁这个队列
        result = self.channel.queue_declare(exclusive=True)
        # 声明请求响应回执的queue，获取上面创建的队列名字，就是那个随机值
        self.callback_queue = result.method.queue

        self.channel.basic_consume(consumer_callback=self.on_response,  # 当消息来临时，消费者会执行回调函数callback
                                   queue=self.callback_queue, no_ack=True)  # 监听回执queue，这个True用来保证数据不丢失

    def on_response(self, ch, method, props, body):  # callback_queue的回调函数
        logger.info(json.loads(body))
        data = json.loads(body)
        if self.correlation_id == props.correlation_id:
            print("rabbit MQ judge client response: ", data)
            self.response = data

    def call(self, content):
        logger.info(content)
        self.correlation_id = str(uuid.uuid1())
        self.channel.basic_publish(exchange='',
                                   routing_key=Rabbit_MQ_QueueID_Judge,
                                   properties=pika.BasicProperties  # 发送回执消息的参数
                                   (reply_to=self.callback_queue,
                                    correlation_id=self.correlation_id),
                                   body=json.dumps(content)
                                   )
        while self.response is None:
            self.connection.process_data_events()  # 事件驱动，非阻塞版的start_consuming
        return self.response

