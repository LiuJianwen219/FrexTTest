import json
import logging
import os
import subprocess
import time
from datetime import datetime

import requests
from threading import Timer
from django.http import HttpResponse
from apscheduler.schedulers.background import BackgroundScheduler
from django.views.decorators.csrf import csrf_exempt
from Constant import constants as const
from Compile.compile_task import CompileTaskThread, send_task_to_rabbit_mq
from Judge.judger import JudgeThread, JudgeHandleThread, JudgeTimeCounter
from Compile.thread_handler import TaskHandlerThread, TimeCounter
from FrexTTest.settings import userFilesPath, Compile_MAX_Thread, Compile_MAX_Time, Judge_MAX_Time
from Home.models import TestList, SubmitList

logger = logging.getLogger(__name__)

# Create your views here.

compile_checker = None
threadIndex = 0
threadList = {}

# judgeChecker = None
# judgeThreadIndex = 0
# judgeThreadList = {}

countCom = 0
# countJud = 0


def start_compile(request):
    t_uid = request.POST.get("t_uid", None)
    s_uid = request.POST.get("s_uid", None)
    test = TestList.objects.get(uid=t_uid)
    if request.method == "POST":
        content = {
            'userId': request.session['u_uid'],
            'testId': t_uid,
            'submitId': s_uid,
            'topic': test.topic,
            'topModuleName': test.top_module_name,
        }

        # 只需要将编译任务丢到rabbitmq队列里面
        # 开启一个线程进行计时，目前认为超过1个小时则表示编译超时，前端进行展示超时信息
        # 后台中断等待
        # utilities = ZipUtilities()
        # path = os.path.join(userFilesPath, content['userName'], content['fid'], content['count'])
        # filenames = os.listdir(path)
        # for filename in filenames:
        #     filepath = os.path.join(path, filename)
        #     utilities.toZip(filepath, filename)
        # z = utilities.zip_file
        # z.write(content['tempFilePath'])
        # with open(content['tempFilePath'], 'wb') as f:
        #     for data in z:
        #         f.write(data)
        # print(content['userName'] + " " + request.session['upTime'] + " : zip over")

        global compile_checker
        if not compile_checker:
            compile_checker = BackgroundScheduler()
            compile_checker.add_job(detect_compile, "interval", seconds=5)
            compile_checker.start()
        compile_checker.pause()

        global threadList
        global threadIndex
        if len(threadList) >= Compile_MAX_Thread:  # 表示当前没有编译线程资源
            data = {"state": "OK", "testState": "暂时没有编译线程资源，请稍后重新提交 " + str(threadList), "info": "Waiting"}
            compile_checker.resume()
            return HttpResponse(json.dumps(data), content_type='application/json')

        content['threadIndex'] = str(threadIndex)  # 0
        # threadList[content['threadIndex']] = CompileHandleThread(TaskHandlerThread(CompileTaskThread, content),
        #                                                          TimeCounter(Compile_MAX_Time))  # 0
        threadList[content['threadIndex']] = TaskHandlerThread(
            CompileTaskThread(send_task_to_rabbit_mq, content), TimeCounter(Compile_MAX_Time))
        threadIndex += 1  # 1

        threadList[content['threadIndex']].start()
        print("compile start: " + json.dumps(content))

        # global threadID
        # global threadList
        # threadList[str(threadID)] = CompileThread(compileBit, tempFilePath,
        #                                           testList.objects.get(id=fid).topModule)
        # currentThreadID = threadID
        # threadID += 1
        # threadList[str(currentThreadID)].start()
        # print("start compiler")
        # result = compileBit(tempFilePath, testList.objects.get(id=fid).topModule)
        # result = {'state': "OK", 'bitFilePath': "/tmp/bit/", 'bitFileName': "default_10.bit", 'info': "编译成功"}
        # print(result)
        # logger.warning("编译信息：")
        # if result['state'] == 'OK':
        #     info = "编译完成"
        #     testState = "编译成功，正在测试"
        #     state = "OK"
        #
        #     userDir = userFilesPath + request.session["user_name"] + "/" + fid + "/" + str(count)
        #     logger.warning(os.getcwd())
        #     res, output = subprocess.getstatusoutput(
        #         "cp " + os.path.join(result['bitFilePath'] + "/" + result['bitFileName']) + " " + userDir)
        #
        #     if res == 0:
        #         user = User2.objects.get(name=request.session["user_name"])
        #         test = testList.objects.get(id=fid)
        #         row = upList.objects.get(test=test, user=user, count=request.session["count"])
        #         row.state = testState
        #         row.info = info
        #         row.save()
        #         data = {
        #             "state": state,
        #             "testState": testState,
        #             "bitFileName": result['bitFileName'],
        #             "bitFilePath": userDir,
        #             'info': info
        #         }
        #         return HttpResponse(json.dumps(data), content_type='application/json')
        #
        #     data = {"state": "ERROR", "testState": "数据拷贝出错", "info": "编译失败"}
        #     return HttpResponse(json.dumps(data), content_type='application/json')

        # submit = SubmitList.objects.get(uid=request.session["s_uid"])
        # submit.status = "提交编译任务"
        # submit.message += "Success: code compile task record complete.\n"
        # submit.save()

        compile_checker.resume()

        data = {"state": "OK", "testState": "提交成功，接下来交给后台处理", "info": "task submit"}
        return HttpResponse(json.dumps(data), content_type='application/json')

    data = {"state": "ERROR", "testState": "非POST请求", "info": "task submit error"}
    return HttpResponse(json.dumps(data), content_type='application/json')


def detect_compile():
    global threadList
    global countCom
    if len(threadList) > 0 or countCom < 10:
        print("detect com " + str(len(threadList)))
        if len(threadList) == 0:
            countCom += 1
        else:
            countCom = 0

    needToDel = []
    for key in threadList:
        if threadList[key].get_time() > Compile_MAX_Time:  # 表示编译超时
            print("compile timeout: " + json.dumps(threadList[key].get_contents()))
            submit = SubmitList.objects.get(uid=threadList[key].get_content("submitId"))
            submit.status = "编译超时，请稍后重新提交"
            submit.message += str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())) + " Failed: code compile task time out.\n"
            submit.save()
            needToDel.append(threadList[key].get_content("threadIndex"))
        if threadList[key].get_task_result() is not None:  # 表示编译任务提交到了RabbitMQ
            # print("task submit over: " + json.dumps(threadList[key].get_contents()))
            result = threadList[key].get_task_result()
            # print("task submit over: " + json.dumps(result))
            if result['state'] == 'OK':
                # submit = SubmitList.objects.get(uid=threadList[key].get_content("submitId"))
                # submit.status = "提交编译任务成功"
                # submit.message += "Success: code compile task submit complete.\n"
                # submit.save()
                if not threadList[key].task_thread.is_sub_over():
                    submit = SubmitList.objects.get(uid=threadList[key].get_content("submitId"))
                    submit.status = "提交编译任务成功"
                    submit.message += str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())) + " Success: code compile task submit complete.\n"
                    submit.compile_start_time = datetime.now()
                    submit.save()
                    threadList[key].task_thread.set_sub_over()
                elif threadList[key].task_thread.is_over():
                    needToDel.append(key)
                else:
                    submit = SubmitList.objects.get(uid=threadList[key].get_content("submitId"))
                    submit.status = "提交编译任务成功，编译{0}秒".format(threadList[key].get_time())
                    submit.message += str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())) + " Running: compile {0} seconds\n".format(threadList[key].get_time())
                    submit.save()
            else:
                submit = SubmitList.objects.get(uid=threadList[key].get_content("submitId"))
                submit.status = "提交编译任务失败，请重新提交"
                submit.message += str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())) + " Failed: code compile task submit error.\n"
                submit.compile_end_time = datetime.now()
                submit.save()
                needToDel.append(key)
        threadList[key].time_add()


    for k in needToDel:
        print("compile thread delete: " + json.dumps(threadList[k].get_contents()))
        del threadList[k]


@csrf_exempt
def compile_result(request):
    if request.method == "POST":
        values = {
            "userId":       request.POST.get("userId", None),
            "testId":       request.POST.get("testId", None),
            "submitId":     request.POST.get("submitId", None),
            "topic":        request.POST.get("topic", None),
            "state":        request.POST.get("state", None),
            "status":       request.POST.get("status", None),
            "message":      request.POST.get("message", None),
            "threadIndex":  request.POST.get("threadIndex", None),
        }
        # print(values)
        # print(values["status"])
        global threadList
        if values["status"] == "编译成功":
            url = const.file_server_url + const.rpts_API + "/"
            r = requests.get(url, params=values)
            if r.status_code.__str__() != "200":
                logger.error("Request RPT failed: " + r.headers.__str__())
                return const.request_failed

            # data from compile files .rpt
            index_luts = r.content.__str__().find("Slice LUTs")
            strs_luts = r.content.__str__()[index_luts:r.content.__str__().find("\\n", index_luts)].split("|")

            # data from compile files .rpt
            index_ff = r.content.__str__().find("Slice Registers")
            strs_ff = r.content.__str__()[index_ff:r.content.__str__().find("\\n", index_ff)].split("|")

            submit = SubmitList.objects.get(uid=values["submitId"])
            submit.status = values["status"]
            submit.message += values["message"] + "\n"
            submit.compile_end_time = datetime.now()
            submit.lut_count = int(strs_luts[1])
            submit.ff_count = int(strs_ff[1])
            submit.comTime = threadList[values["threadIndex"]].get_time()
            submit.save()
            threadList[values["threadIndex"]].task_thread.set_over()

            r = requests.post(url="http://frext-testing-svc:8030/judge/startJudge/", data=values)
            if r.status_code.__str__() == "200":
                logger.error("Request Result success: " + r.headers.__str__())
            else:
                logger.error("Request Result failed: " + r.headers.__str__())
        else:
            logger.warning("compile status: " + values["status"])
            logger.warning("compile message: " + values["message"])
            submit = SubmitList.objects.get(uid=values["submitId"])
            submit.status = "编译失败"
            submit.message += values["message"] + "\n"
            submit.compile_end_time = datetime.now()
            submit.comTime = threadList[values["threadIndex"]].get_time()
            submit.save()
            threadList[values["threadIndex"]].task_thread.set_over()

        data = {"state": "OK", "testState": "", "info": ""}
        return HttpResponse(json.dumps(data), content_type='application/json')

    data = {"state": "ERROR", "testState": "非POST请求", "info": "task submit error"}
    return HttpResponse(json.dumps(data), content_type='application/json')
