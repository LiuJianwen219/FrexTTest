import decimal
from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler
from django.shortcuts import render
import os, json, time
import subprocess, uuid
from threading import Timer

from django.core.files import File
from django.db.models import Sum, Count, Max
from django.http import HttpResponse, JsonResponse, FileResponse
from django.shortcuts import render, redirect

# Create your views here.
# from Test import forms
# from Test.RocketMQHandler import RabbitMQHandler
# from Test.ZipUtilities import ZipUtilities
# from Test.compiler import compileBit, CompileThread, CompileHandleThread, TimeCounter
# from Test.judger import JudgeThread, exection, JudgeHandleThread, JudgeTimeCounter
# from Test.models import testList, fileList, upList, passList, gradeList
# from exoticTest.settings import userFilesPath, compileErrPath, testFilesPath, compileZipPath, compileBitPath, \
#     Compile_MAX_Thread, Compile_MAX_Time, Judge_MAX_Time
from django.template.defaulttags import now
from django.views.decorators.csrf import csrf_exempt

from Home.models import SubmitList, TestList, ValidSubmitList, BestSubmitList
from Judge.judger import JudgeHandleThread, JudgeThread, JudgeTimeCounter, execution
from FrexTTest.settings import Judge_MAX_Time

import logging

from Login.models import User

logger = logging.getLogger(__name__)

judgeChecker = None
judgeThreadIndex = 0
judgeThreadList = {}

countCom = 0
countJud = 0


# Create your views here.

@csrf_exempt
def start_judge(request):
    print("start_judge: ")

    global judgeChecker
    if judgeChecker is None:
        judgeChecker = BackgroundScheduler()
        judgeChecker.add_job(detectJudge, "interval", seconds=10)
        judgeChecker.start()
    judgeChecker.pause()


    values = {
        "userId": request.POST.get("userId", None),
        "testId": request.POST.get("testId", None),
        "submitId": request.POST.get("submitId", None),
        "topic": request.POST.get("topic", None),
        "state": request.POST.get("state", None),
        "status": request.POST.get("status", None),
        "message": request.POST.get("message", None),
    }
    print("start_judge: ", values)

    # content = {
    #     'fid': input["fid"],
    #     'count': input["count"],
    #     'userName': input["userName"],
    #     'bitFileName': input['bitFileName']
    # }

    global judgeThreadIndex
    global judgeThreadList
    # if len(judgeThreadList) < Judge_MAX_Thread  # ????????????????????????????????????????????????????????????RabbitMQ

    values['judgeThreadIndex'] = str(judgeThreadIndex)
    judgeThreadList[values['judgeThreadIndex']] = JudgeHandleThread(JudgeThread(execution, values), JudgeTimeCounter())
    judgeThreadIndex += 1

    judgeThreadList[values['judgeThreadIndex']].start()
    print("judge start: " + values['judgeThreadIndex'])

    submit = SubmitList.objects.get(uid=values["submitId"])
    submit.status = "????????????"
    submit.message += str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())) + " Start: test\n"
    submit.test_start_time = datetime.now()
    submit.save()

    judgeChecker.resume()

    data = {"state": "OK", "testState": "????????????", "info": "task submit"}
    return HttpResponse(json.dumps(data), content_type='application/json')


def detectJudge():
    global judgeThreadList

    global countJud
    if len(judgeThreadList) > 0 or countJud < 3:
        print("detect judge " + str(len(judgeThreadList)))
        if len(judgeThreadList) == 0:
            countJud += 1
        else:
            countJud = 0

    needToDel = []

    # global judgeThreadList
    for key in judgeThreadList:
        print(time.time())
        if judgeThreadList[key].get_time() > Judge_MAX_Time:
            print("judge timeout: " + key)
            submitId = judgeThreadList[key].get_content("submitId")
            submit = SubmitList.objects.get(uid=submitId)
            submit.status = "??????????????????"
            submit.message += str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())) + " Timeout: test\n"
            submit.test_end_time = datetime.now()
            submit.save()

            needToDel.append(key)
        elif judgeThreadList[key].get_judge() is not None:
            print("judge end: " + key)
            submitId = judgeThreadList[key].get_content("submitId")
            testId = judgeThreadList[key].get_content("testId")
            userId = judgeThreadList[key].get_content("userId")
            submit = SubmitList.objects.get(uid=submitId)
            test = TestList.objects.get(uid=testId)
            user = User.objects.get(uid=userId)

            r, cycle, testResult = judgeThreadList[key].get_judge()
            submit.exeTime = judgeThreadList[key].get_time()

            if r == 0:
                result = json.dumps(testResult)
                status = "????????????????????????"
                message = str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())) + " Success: test is complete.\n"
                cnt = 0
                for res in testResult:
                    if res['result'] == "????????????":
                        cnt = cnt + 1
                grade = round(decimal.Decimal(cnt / len(testResult)) * test.grade, 2)
                state = "try"
                if cnt == len(testResult):
                    state = "pass"
            else:
                result = ""
                status = "??????????????????????????????????????????????????????"
                message = str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())) + " Failed: test is not complete.\n"
                grade = 0.00
                state = "try"

            submit.state = state
            submit.status = status
            submit.score = grade
            submit.result = result
            submit.cycle = cycle
            submit.message += message
            submit.test_end_time = datetime.now()
            submit.save()

            if state == "pass":
                test.pass_number += 1  # ?????????????????? +1
                test.save()
                # ?????????????????????????????????????????????
                v_submits = ValidSubmitList.objects.filter(test=test, user=user)
                if len(v_submits) == 0:
                    v_submit = ValidSubmitList()
                    v_submit.user = user
                    v_submit.test = test
                    v_submit.submit = submit
                    v_submit.save()
                elif cycle < v_submits[0].submit.cycle:
                    v_submits[0].submit = submit
                    v_submits[0].save()

            if grade > 0.0:
                # ???????????????????????????????????????????????????
                b_submits = BestSubmitList.objects.filter(test=test, user=user)
                if len(b_submits) == 0:
                    b_submit = BestSubmitList()
                    b_submit.user = user
                    b_submit.test = test
                    b_submit.submit = submit
                    b_submit.save()
                elif grade > b_submits[0].submit.score:
                    b_submits[0].submit = submit
                    b_submits[0].save()

            needToDel.append(key)
        else:
            submitId = judgeThreadList[key].get_content("submitId")
            submit = SubmitList.objects.get(uid=submitId)
            submit.status = "?????????????????????{0}???".format(judgeThreadList[key].get_time())
            submit.message += str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())) + \
                              " Running: testing {0} seconds\n".format(judgeThreadList[key].get_time())

    for k in needToDel:
        print("judge delete: " + k)
        del judgeThreadList[k]



def judge_result(request):
    return None
