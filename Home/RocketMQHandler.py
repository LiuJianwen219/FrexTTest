import uuid
import pika
import json
from FrexTTest.settings import Rabbit_MQ_IP, Rabbit_MQ_QueueID
from FrexTTest.settings import Rabbit_MQ_USER, Rabbit_MQ_PASS, Rabbit_MQ_Port, Rabbit_MQ_VHOST


class RabbitMQHandler:
    def __init__(self):
        self.auth = pika.PlainCredentials(Rabbit_MQ_USER, Rabbit_MQ_PASS)
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=Rabbit_MQ_IP, port=Rabbit_MQ_Port,
                                      virtual_host=Rabbit_MQ_VHOST, credentials=self.auth,
                                      heartbeat_interval=0))
        self.channel = self.connection.channel()

        result = self.channel.queue_declare(exclusive=True)  # 定义一个队列，随机取名，但是当本进程结束后自动销毁这个队列
        # result = self.channel.queue_declare(exclusive=True, durable=True)  # 定义一个队列，随机取名，但是当本进程结束后自动销毁这个队列
        self.callback_queue = result.method.queue  # 声明请求响应回执的queue，获取上面创建的队列名字，就是那个随机值

        self.channel.basic_consume(consumer_callback=self.on_response,  # 当消息来临时，消费者会执行回调函数callback
                                   queue=self.callback_queue, no_ack=True)  # 监听回执queue，这个True用来保证数据不丢失

    def on_response(self, ch, method, props, body):  # callback_queue的回调函数
        print(json.loads(body))
        if self.corr_id == props.correlation_id:
            if json.loads(body)['info'] == "测试正常":
                self.response = [0, json.loads(body)['usingCycle'],
                                 json.loads(body)['testResult'], json.loads(body)['info']]
            else:
                self.response = [-1, json.loads(body)['usingCycle'],
                                 json.loads(body)['testResult'], json.loads(body)['info']]

    def call(self, content):
        # print(content)
        self.response = None
        self.corr_id = str(uuid.uuid4())
        self.channel.basic_publish(exchange='',
                                   routing_key=Rabbit_MQ_QueueID,
                                   properties=pika.BasicProperties  # 发送回执消息的参数
                                   (reply_to=self.callback_queue,
                                    correlation_id=self.corr_id),
                                   body=json.dumps(content)
                                   )
        while self.response is None:
            self.connection.process_data_events()  # 事件驱动，非阻塞版的start_consuming
        return self.response

