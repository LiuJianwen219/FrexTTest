import logging
import sys
import json
import pika
import requests
import tornado
from constant import *

sys.path.append('../')
logger = logging.getLogger(__name__)
from FrexTTest.settings import Rabbit_MQ_IP, Rabbit_MQ_Port, Rabbit_MQ_VHOST
from FrexTTest.settings import Rabbit_MQ_USER, Rabbit_MQ_PASS

from FrexTTest.settings import Rabbit_MQ_QueueID_Compile
from FrexTTest.settings import Compile_Server_Url, Compile_Server_Api
from FrexTTest.settings import Compile_MAX_Thread

from FrexTTest.settings import Rabbit_MQ_QueueID_Judge
from FrexTTest.settings import Judge_Server_Url, Judge_Server_Api
from FrexTTest.settings import Judge_MAX_Thread


class CompileRabbitMQServer:
    def __init__(self):
        # self.connect = pika.BlockingConnection(pika.ConnectionParameters(host=Rabbit_MQ_IP))  # 连接 RabbitMQ
        # self.channel = self.connect.channel()  # 获取一个通道
        self.auth = pika.PlainCredentials(Rabbit_MQ_USER, Rabbit_MQ_PASS)
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=Rabbit_MQ_IP, port=Rabbit_MQ_Port,
                                      virtual_host=Rabbit_MQ_VHOST, credentials=self.auth))
        self.channel = self.connection.channel()

        self.channel.queue_declare(queue=Rabbit_MQ_QueueID_Compile)  # 定义一个队列，取名为rpc_queue
        # channel.queue_declare(queue='rpc_queue', durable=True) # 定义一个队列，取名为rpc_queue，消息持久化（只保存了队列）
        self.channel.basic_qos(prefetch_count=Compile_MAX_Thread)  # 限制消息处理个数
        self.channel.basic_consume(self.on_request, queue=Rabbit_MQ_QueueID_Compile)

        print('testing compile process is waiting...')
        self.channel.start_consuming()

    def on_request(self, ch, method, props, body):
        response = self.work_process(json.loads(body))
        logger.info("compile work_process response: ", response)
        print("rabbit MQ server response " + response)

        ch.basic_publish(exchange='',  # exchange是发送端特有的
                         routing_key=props.reply_to,
                         properties=pika.BasicProperties(correlation_id=props.correlation_id),
                         # properties=pika.BasicProperties(delivery_mode=2)),  # 保持消息持久化
                         body=str(response))
        print('compile send over')
        ch.basic_ack(delivery_tag=method.delivery_tag)  # 确认client接收到消息

    def work_process(self, content):
        logger.info("compile work_process request: ", content)
        print(content)
        # 这里要进行CompileServer负载考虑
        # 并进行编译请求
        # 但是这里仅仅是请求，正常能够立马收到回复
        # 编译完成后，CompileServer会请求web的一个http接口，回复编译结果
        url = Compile_Server_Url + Compile_Server_Api
        r = requests.post(url=url, params=content, data=content)
        print(r.content)
        response = json.loads(r.content.decode())
        data = {'state': response['state'], 'message': response['message'], 'content': response['content']}
        # data = {'state': "OK", 'testResult': testResult, "usingCycle": cycle, "info": info}
        return json.dumps(data)


CompileServer = CompileRabbitMQServer()


class JudgeRabbitMQServer:
    def __init__(self):
        # self.connect = pika.BlockingConnection(pika.ConnectionParameters(host=Rabbit_MQ_IP))  # 连接 RabbitMQ
        # self.channel = self.connect.channel()  # 获取一个通道
        self.auth = pika.PlainCredentials(Rabbit_MQ_USER, Rabbit_MQ_PASS)
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=Rabbit_MQ_IP, port=Rabbit_MQ_Port,
                                      virtual_host=Rabbit_MQ_VHOST, credentials=self.auth))
        self.channel = self.connection.channel()

        self.channel.queue_declare(queue=Rabbit_MQ_QueueID_Judge)  # 定义一个队列，取名为rpc_queue
        # channel.queue_declare(queue='rpc_queue', durable=True) # 定义一个队列，取名为rpc_queue，消息持久化（只保存了队列）
        self.channel.basic_qos(prefetch_count=Judge_MAX_Thread)  # 限制消息处理个数
        self.channel.basic_consume(self.on_request, queue=Rabbit_MQ_QueueID_Judge)

        print('testing judge process is waiting...')
        self.channel.start_consuming()

    def on_request(self, ch, method, props, body):
        response = self.work_process(json.loads(body))
        logger.info("judge work_process response: ", response)
        print("judge work_process response: ", response)

        ch.basic_publish(exchange='',  # exchange是发送端特有的
                         routing_key=props.reply_to,
                         properties=pika.BasicProperties(correlation_id=props.correlation_id),
                         # properties=pika.BasicProperties(delivery_mode=2)),  # 保持消息持久化
                         body=str(response))
        print('judge send over')
        ch.basic_ack(delivery_tag=method.delivery_tag)  # 确认client接收到消息

    def work_process(self, content):
        logger.info("judge work_process request: ", content)
        print("judge work_process request: ", content)
        # 这里要进行 JudgeServer负载考虑，包括开发板的占用情况，测试实验比例，可能还要根据时段进行不同的比例策略
        # 但是这里仅仅是请求开发板，正常能够立马收到回复
        #   测试完成后，会请求web的一个http接口，回复编译结果
        #   实验完成后，会返回一个信息，标志开发板回到空闲状态
        url = Judge_Server_Url + Judge_Server_Api
        r = requests.post(url=url, params=content, data=content)
        print(r.content)
        response = json.loads(r.content.decode())
        data = {'state': response['state'], 'message': response['message'], 'content': response['content']}
        # data = {'state': "OK", 'testResult': testResult, "usingCycle": cycle, "info": info}
        return json.dumps(data)


JudgeServer = JudgeRabbitMQServer()
