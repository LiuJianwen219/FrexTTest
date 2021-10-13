import time
import websocket
import pika
import json, sys
import logging
from constant import *

sys.path.append('../')
logger = logging.getLogger(__name__)
from FrexTTest.settings import Rabbit_MQ_IP, Socker_Server_IP, Rabbit_MQ_Port, Rabbit_MQ_USER, Rabbit_MQ_PASS, \
    Rabbit_MQ_VHOST
from FrexTTest.settings import Socker_Server_Port, Rabbit_MQ_QueueID_Judge, Judge_MAX_Thread

# deviceNum = 10
# bitFilePath="/tmp/123.bit"

testResultGlobal = None
usingCycle = None
infoGlobal = None


class RabbitMQHandler:
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

        print('testing process is waiting...')
        self.channel.start_consuming()

    def work_process(self, content):
        print(json.loads(content))
        content = json.loads(content)

        # url = "http://" + "10.14.30.15" + ":" + "8000" + "/test/download/?deviceId=" + \
        #      str(deviceNum) + "&userId=" + content["userId"] + "&type=" + content["type"] + \
        #      "&fid=" + content["fid"] + "&count=" + str(content["count"]) + "&fileName=" + content["fileName"]
        # r = requests.get(url)  # create HTTP response object
        # print(url)
        # result = rpi.programBit()  # program the constant filepath
        # for i in range(0, 5):
        #    print(i)
        #    time.sleep(1)

        webhandler = WebHandle(content)
        webhandler.start()

        testResult = [{"index": 0, "result": "测试通过", "info": "正确"},
                      {"index": 1, "result": "答案错误", "info": "0x40!=0x44"}]
        cycle = -1

        info = None

        global testResultGlobal
        if testResultGlobal is not None:
            testResult = testResultGlobal
        global usingCycle
        if usingCycle is not None:
            cycle = usingCycle
        global infoGlobal
        if infoGlobal is not None:
            info = infoGlobal

        data = {'state': "OK", 'testResult': testResult, "usingCycle": cycle, "info": info}
        return json.dumps(data)

    def on_request(self, ch, method, props, body):
        response = self.work_process(body)
        print("response " + str(response))

        ch.basic_publish(exchange='',  # exchange是发送端特有的
                         routing_key=props.reply_to,
                         properties=pika.BasicProperties(correlation_id=props.correlation_id),
                         # properties=pika.BasicProperties(delivery_mode=2)),  # 保持消息持久化
                         body=str(response))
        print('send over')
        ch.basic_ack(delivery_tag=method.delivery_tag)  # 确认client接收到消息


class WebHandle:
    def __init__(self, content):
        self.ws = websocket.WebSocketApp("ws://" + Socker_Server_IP + ":" + str(Socker_Server_Port),
                                         on_message=self.on_message,
                                         on_error=self.on_error,
                                         on_close=self.on_close,
                                         on_open=self.on_open)
        self.content = content

    def on_open(self):
        print("RABBIT on open")

    def on_message(self, message):
        print(message)
        dict_ = json.loads(message)
        if dict_["type"] == WHO_YOU_ARE:
            data = {
                'type': AUTH_RABBIT,
            }
            print("AUTH_RABBIT")
            self.ws.send(json.dumps(data))
        elif dict_["type"] == AUTH_RABBIT_FAIL:
            print(dict_['info'])
            exit(-1)
        elif dict_["type"] == AUTH_RABBIT_SUCC:
            print("AUTH_RABBIT_SUCC")
            data = {'type': ACT_SYNC}  # 对设备使用情况进行同步
            self.ws.send(json.dumps(data).encode("utf-8"))

        elif dict_["type"] == SYNC_DEVICE:
            print("SYNC_DEVICE")
            nReady = dict_['content']['nReady']
            if nReady > 0:
                data = {'type': ACT_ACQUIRE, 'using': "TEST"}
                self.ws.send(json.dumps(data).encode("utf-8"))
            else:
                time.sleep(3)  # 如果获取设备失败的话，那么停一秒钟重新获取
                print("ACT_SYNC")
                data = {'type': ACT_SYNC}  # 对设备使用情况进行同步
                self.ws.send(json.dumps(data).encode("utf-8"))
        elif dict_["type"] == ACQUIRE_SUCC:
            print("TEST_REQ_DEVICE_SUCC")
            data = {'type': TEST_PROGRAM, 'content': self.content}
            self.ws.send(json.dumps(data).encode("utf-8"))


        elif dict_["type"] == TEST_PROGRAM_SUCC:
            print("TEST_PROGRAM_SUCC")
            data = {'type': TEST_READ_RESULT}
            self.ws.send(json.dumps(data).encode("utf-8"))
        elif dict_["type"] == TEST_PROGRAM_FAIL:
            print("TEST_PROGRAM_FAIL???")
            self.ws.close()

        elif dict_["type"] == TEST_READ_RESULT_SUCC:
            print("TEST_READ_RESULT_SUCC")
            if dict_['testStatus'] == "Complete":
                global testResultGlobal
                testResultGlobal = dict_['testResult']
                global usingCycle
                usingCycle = dict_['usingCycle']
                global infoGlobal
                infoGlobal = dict_['info']
                print(dict_['testResult'])  ###########################
            self.ws.close()

    def on_error(self, error):
        print("rabbitMQ Socket ERROR: " + error)

    def on_close(self):
        print("### closed ###")

    def start(self):
        print("start testing ... ...")
        self.ws.run_forever()


rabbitMQHandler = RabbitMQHandler()
