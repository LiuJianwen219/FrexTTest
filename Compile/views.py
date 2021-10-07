import json
import logging
import os
import subprocess
from datetime import datetime

import requests
from threading import Timer
from django.http import HttpResponse
from apscheduler.schedulers.background import BackgroundScheduler
from django.views.decorators.csrf import csrf_exempt

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
    if request.method == "POST":
        content = {
            'userId': request.session['u_uid'],
            'testId': request.session["t_uid"],
            'submitId': request.session["s_uid"],
            'topic': TestList.objects.get(uid=request.session["t_uid"]).topic,
            'topModuleName': TestList.objects.get(uid=request.session["t_uid"]).top_module_name,
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
            submit.message += "Failed: code compile task time out.\n"
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
                    submit.message += "Success: code compile task submit complete.\n"
                    submit.compile_start_time = datetime.now()
                    submit.save()
                    threadList[key].task_thread.set_sub_over()
                elif threadList[key].task_thread.is_over():
                    needToDel.append(key)
                else:
                    submit = SubmitList.objects.get(uid=threadList[key].get_content("submitId"))
                    submit.status = "提交编译任务成功，编译{0}秒".format(threadList[key].get_time())
                    submit.message += "Running: compile {0} seconds\n".format(threadList[key].get_time())
                    submit.save()
            else:
                submit = SubmitList.objects.get(uid=threadList[key].get_content("submitId"))
                submit.status = "提交编译任务失败，请重新提交"
                submit.message += "Failed: code compile task submit error.\n"
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
        print(values)
        print(values["status"])
        submit = SubmitList.objects.get(uid=values["submitId"])
        submit.status = values["status"]
        submit.message = submit.message + values["message"] + "\n"
        submit.compile_end_time = datetime.now()
        global threadList
        submit.comTime = threadList[values["threadIndex"]].get_time()
        submit.save()
        threadList[values["threadIndex"]].task_thread.set_over()

        # if values['status'] == "编译成功":
        # 发起测试请求
        r = requests.post(url="http://frext-testing-svc:8030/judge/startJudge/", data=values)
        # 更新数据库
        if r.status_code.__str__() == "200":
            logger.error("Request Result success: " + r.headers.__str__())
        else:
            logger.error("Request Result failed: " + r.headers.__str__())

        data = {"state": "OK", "testState": "", "info": ""}
        return HttpResponse(json.dumps(data), content_type='application/json')

    data = {"state": "ERROR", "testState": "非POST请求", "info": "task submit error"}
    return HttpResponse(json.dumps(data), content_type='application/json')



def detectCompile():
    global threadList

    global countCom
    if len(threadList) > 0 or countCom < 3:
        print("detect com " + str(len(threadList)))
        if len(threadList) == 0:
            countCom += 1
        else:
            countCom = 0

    startJudgeCount = 0
    startJudgeContent = []

    needToDel = []
    # global threadList
    for key in threadList:
        # print(key + ':' + threadList[key])
        if threadList[key].get_time() > Compile_MAX_Time:  # 表示编译超时
            print("compile timeout: " + key)
            fid = threadList[key].get_content("fid")
            count = threadList[key].get_content("count")
            userName = threadList[key].get_content("userName")
            user = User2.objects.get(name=userName)
            test = testList.objects.get(id=fid)
            row = upList.objects.get(test=test, user=user, count=int(count))
            row.state = "编译失败"
            row.info = "编译超时"
            row.save()

            needToDel.append(threadList[key].get_content("threadIndex"))

        if threadList[key].get_compile() is not None:  # 表示编译完成得到结果
            print("compile end: " + key)
            fid = threadList[key].get_content("fid")
            count = threadList[key].get_content("coSubmitListunt")
            userName = threadList[key].get_content("userName")
            user = User2.objects.get(name=userName)
            test = testList.objects.get(id=fid)
            row = upList.objects.get(test=test, user=user, count=int(count))

            result = threadList[key].get_compile()
            userDir = userFilesPath + userName + "/" + fid + "/" + str(count)
            row.comTime = threadList[key].get_time()
            if result['state'] == 'OK':
                res, output = subprocess.getstatusoutput(
                    "cp " + os.path.join(result['bitFilePath'] + "/" + result['bitFileName']) + " " + userDir)

                # {'state': "OK", 'bitFilePath': tempFilePath, 'bitFileName': tempFileName, 'info': "编译成功"}

                # row.comTime = threadList[key].get_time()

                if res == 0:
                    row.state = "编译成功，准备测试"
                    row.info = "编译完成"
                    row.save()

                    startJudgeCount += 1
                    startJudgeContent.append(threadList[key].get_contents())

            else:
                res, output = subprocess.getstatusoutput(
                    "cp " + os.path.join(result['logFilePath'] + "/" + result['logFileName']) + " " + userDir)
                if res == 0:
                    row.state = result['compileInfo']
                    row.info = "编译失败"
                    row.save()
                else:
                    row.state = "找不到log文件错误"
                    row.info = "编译失败"
                    row.save()

            needToDel.append(threadList[key].get_content("threadIndex"))

    for k in needToDel:
        print("compile delete: " + k)
        del threadList[k]

    for c in startJudgeContent:
        startJudge(c)

    Timer(10, detectCompile).start()


def startJudge(input):
    global judgeChecker
    if judgeChecker is None:
        judgeChecker = 1
        Timer(10, detectJudge).start()

    content = {
        'fid': input["fid"],
        'count': input["count"],
        'userName': input["userName"],
        'bitFileName': input['bitFileName']
    }

    global judgeThreadIndex
    global judgeThreadList
    # if len(judgeThreadList) < Judge_MAX_Thread  # 测试不需要等待，因为总是将评测任务发送给RabbitMQ

    content['judgeThreadIndex'] = str(judgeThreadIndex)
    judgeThreadList[content['judgeThreadIndex']] = JudgeHandleThread(JudgeThread(exection, content), JudgeTimeCounter())
    judgeThreadIndex += 1

    judgeThreadList[content['judgeThreadIndex']].start()
    print("judge start: " + content['judgeThreadIndex'])

    user = User2.objects.get(name=input['userName'])
    test = testList.objects.get(id=input['fid'])
    row = upList.objects.get(test=test, user=user, count=int(input['count']))
    row.state = "开启评测"
    row.info = "开始评测线程"
    row.save()


def detectJudge():
    global judgeThreadList

    global countJud
    if len(judgeThreadList) > 0 or countJud < 10:
        print("detect judge " + str(len(judgeThreadList)))
        if len(judgeThreadList) == 0:
            countJud += 1
        else:
            countJud = 0

    needToDel = []

    # global judgeThreadList
    for key in judgeThreadList:
        if judgeThreadList[key].get_time() > Judge_MAX_Time:
            print("judge timeout: " + key)
            fid = judgeThreadList[key].get_content("fid")
            count = judgeThreadList[key].get_content("count")
            userName = judgeThreadList[key].get_content("userName")
            user = User2.objects.get(name=userName)
            test = testList.objects.get(id=fid)
            row = upList.objects.get(test=test, user=user, count=int(count))
            row.state = "测试失败"
            row.info = "测试超时"
            row.save()

            needToDel.append(key)

        if judgeThreadList[key].get_judge() is not None:
            print("judge end: " + key)
            fid = judgeThreadList[key].get_content("fid")
            count = judgeThreadList[key].get_content("count")
            userName = judgeThreadList[key].get_content("userName")
            user = User2.objects.get(name=userName)
            test = testList.objects.get(id=fid)
            row = upList.objects.get(test=test, user=user, count=int(count))

            result, cycle, testResult = judgeThreadList[key].get_judge()
            row.exeTime = judgeThreadList[key].get_time()

            if result == 0:
                info = testResult
                resultShow = json.dumps(testResult)
                testState = "测试流程执行完成"
                cnt = 0
                for res in testResult:
                    if res['result'] == "答案正确":
                        cnt = cnt + 1
                grade = round(cnt / len(testResult) * test.grade, 2)
                judge = "尝试"
                if cnt == len(testResult):
                    judge = "通过"
            else:
                info = "未知错误"
                resultShow = ""
                testState = "测试流程失败（测试超时，请检查代码）"
                grade = 0.00
                judge = "尝试"

            row.state = testState
            row.info = info
            row.grade = grade
            row.judge = judge
            row.cycle = cycle
            row.result = resultShow
            row.save()

            if judge == "通过":
                test.passNum += 1  # 测试通过数目 +1
                test.save()
                # 修改，通过条件下用时最少的代码
                passRecords = passList.objects.filter(test=test, user=user)
                if len(passRecords) == 0:
                    passRecord = passList()
                    passRecord.user = user
                    passRecord.test = test
                    passRecord.grade = grade
                    # passRecord.passTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                    passRecord.leastCycle = cycle
                    passRecord.passCode = row.upCode
                    passRecord.info = row.info
                    passRecord.save()
                elif cycle < passRecords[0].leastCycle:
                    # passRecords[0].passTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                    passRecords[0].leastCycle = cycle
                    passRecords[0].passCode = row.upCode
                    passRecords[0].info = row.info
                    passRecords[0].save()

            if grade > 0.0:
                # 修改有得分的提交里，最高得分的情况
                gradeRecords = gradeList.objects.filter(test=test, user=user)
                if len(gradeRecords) == 0:
                    gradeMax = gradeList()
                    gradeMax.user = user
                    gradeMax.test = test
                    gradeMax.maxGrade = grade
                    gradeMax.passCode = row.upCode
                    gradeMax.info = row.info
                    gradeMax.save()
                elif grade > gradeRecords[0].maxGrade:
                    gradeRecords[0].maxGrade = grade
                    gradeRecords[0].passCode = row.upCode
                    gradeRecords[0].info = row.info
                    gradeRecords[0].save()

            needToDel.append(key)

    for k in needToDel:
        print("judge delete: " + k)
        del judgeThreadList[k]

    Timer(10, detectJudge).start()
