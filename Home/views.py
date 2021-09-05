import os, json, time
import subprocess, uuid
from threading import Timer

from django.core.files import File
from django.db.models import Sum, Count, Max
from django.http import HttpResponse, JsonResponse, FileResponse
from django.shortcuts import render, redirect

# Create your views here.
from Login.models import User
from Home import forms
from Home.RocketMQHandler import RabbitMQHandler
from Home.ZipUtilities import ZipUtilities
from Home.compile import compileBit, CompileThread, CompileHandleThread, TimeCounter
from Home.judger import JudgeThread, exection, JudgeHandleThread, JudgeTimeCounter
from Home.models import TestList, TestFile, SubmitList, ValidSubmitList, BestSubmitList
from FrexTTest.settings import userFilesPath, compileErrPath, testFilesPath, compileZipPath, compileBitPath, \
    Compile_MAX_Thread, Compile_MAX_Time, Judge_MAX_Time

import logging

logger = logging.getLogger(__name__)

compileChecker = None
threadIndex = 0
threadList = {}

judgeChecker = None
judgeThreadIndex = 0
judgeThreadList = {}

countCom = 0
countJud = 0


def handle_uploaded_file(p, f):
    with open(p, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)


def building(request):
    return render(request, "building.html")


def enter_exotic(request):
    return render(request, "building.html")


def test_introduce(request):
    return render(request, "TestHome/testIntroduce.html")


def test_list(request):
    testLists = []
    allTests = TestList.objects.filter()
    for i in allTests:
        testLists.append({"title": i.title, "type": i.type,
                          "grade": i.grade, "passNum": i.pass_number,
                          "upNum": i.submit_number, "id": i.uid,
                          "visibility": i.visibility})
    content = {
        'testList': testLists
    }
    print(content)
    return render(request, "TestHome/testList.html", content)


def test_page(request, uid):
    testItem = TestList.objects.get(id=uid)

    file = open(testFilesPath + str(uid) + "/" +
                testItem.topModule + ".md", 'r', encoding='utf-8')
    testFile = file.read()
    file.close()

    content = {
        "testFile": testFile,
        "type": testItem.type,
        "title": testItem.title,
        "author": testItem.author,
        "company": testItem.company,
        "fid": uid,
        "grade": testItem.grade,
    }

    return render(request, "TestHome/testPage.html", content)


def show_last(request):
    if request.method == "POST":
        uid = request.POST.get("uid", None)
        print("show_last: uid ", uid)
        test = TestList.objects.get(uid=uid)
        user = User.objects.get(name=request.session["user_name"])
        upRecords = SubmitList.objects.filter(test=test, user=user).order_by("upTime")

        upRecord = upRecords.last()
        data = {"state": "OK", "upTime": upRecord.upTime, "testState": upRecord.state,
                "recvCode": upRecord.upCode, "testGrade": upRecord.grade}
        if upRecord.result:
            data["testResult"] = json.loads(upRecord.result)

        return JsonResponse(data)
    data = {"state": "ERROR", "testState": "未知错误，请联系管理员", "info": "非法请求"}
    return JsonResponse(data)


def add_test(request):
    if request.method == "POST":
        if request.session['is_login'] and request.session['role'] == 'admin':
            newTest_form = forms.NewTestForm(request.POST, request.FILES)
            print(newTest_form)
            print(newTest_form.is_valid())
            if newTest_form.is_valid():
                testType = str(newTest_form.cleaned_data.get('testType')).isdecimal()
                grade = str(newTest_form.cleaned_data.get('grade')).isdecimal()
                topic = str(newTest_form.cleaned_data.get('topic')).isalnum()
                topModule = str(newTest_form.cleaned_data.get('testTopName')).isalnum()
                if testType and grade and topModule:
                    if newTest_form.cleaned_data.get('testType') == 1:
                        testType = "combination"
                    elif newTest_form.cleaned_data.get('testType') == 2:
                        testType = "time_sequence"
                    elif newTest_form.cleaned_data.get('testType') == 3:
                        testType = "system_all"
                    else:
                        testType = "undefined"

                    test = TestList()
                    test.title = newTest_form.cleaned_data.get('testName')
                    test.topic = newTest_form.cleaned_data.get('topic')
                    test.top_module_name = newTest_form.cleaned_data.get('testTopName')
                    test.type = newTest_form.cleaned_data.get('testType')
                    test.grade = newTest_form.cleaned_data.get('grade')
                    test.save()
                    if os.path.exists(os.path.join(testFilesPath, str(test.uid))):
                        message = '提交成功！但是路径创建失败！'
                    else:
                        os.makedirs(os.path.join(testFilesPath, str(test.uid)))
                        handle_uploaded_file(os.path.join(testFilesPath, str(test.uid), test.topic+".md"),
                                             request.FILES['file'])
                        test.file_path = os.path.join(testFilesPath, str(test.uid))
                        with open(os.path.join(testFilesPath, str(test.uid), test.topic+".md"), "r") as f:
                            test.content = f.read()
                        test.save()
                        message = '提交成功！'
                    return render(request, "TestHome/addTest.html", locals())
                else:
                    message = '顶层模块名需要是英文，类型和分数必须是数字！'
                    return render(request, "TestHome/addTest.html", locals())
    newTest_form = forms.NewTestForm()
    return render(request, "TestHome/addTest.html", locals())


def add_test_file(request):
    if request.method == "POST":
        if request.session['is_login'] and request.session['role'] == 'admin':
            addTestFile_form = forms.AddTestFileForm(request.POST, request.FILES)
            if addTestFile_form.is_valid():
                values = addTestFile_form.clean()
                print(values)
                test = TestList.objects.get(uid=values.get('topic'))
                files = request.FILES.getlist('files')

                for f in files:
                    ff = TestFile()
                    ff.test = test
                    ff.file_path = os.path.join(test.file_path, f.__str__())
                    handle_uploaded_file(ff.file_path, f)
                    with open(ff.file_path, "r") as tf:
                        ff.content = tf.read()
                    ff.save()

                message = '提交成功！'
                return render(request, "TestHome/addTestFile.html", locals())
            else:
                errors = addTestFile_form.errors
                print(errors)
                message = str(errors)
                return render(request, "TestHome/addTestFile.html", locals())
    addTestFile_form = forms.AddTestFileForm()
    return render(request, "TestHome/addTestFile.html", locals())


def submit_code(request):
    # 完成功能：
    # 1.将用户代码保存到 "/files/userFiles/" + request.session["user_name"] + "/" + fid
    # 2.将用户提交代码的记录保存下来
    # TODO: make this code more safe
    if request.method == "POST":
        t_uid = request.POST.get("uid", None)
        code = request.POST.get("testUserCode", None)

        test = TestList.objects.get(uid=t_uid)
        user = User.objects.get(name=request.session["user_name"])



        info = "创建提交记录"
        # count = SubmitList.objects.filter(test=test, user=user).count()
        state = "ERROR"  # 用于网页通信
        testState = "文件上传失败"  # 用于记录提交情况
        grade = 0.00  # 本次提交的成绩
        # curtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

        row = SubmitList()
        row.save()

        userDir = os.path.join(userFilesPath, "user", request.session["user_name"],
                               "testing", str(t_uid), str(row.uid))
        if not os.path.exists(userDir):  # 如果用户首次提交这个题目的代码，那么创建目录
            os.makedirs(userDir)

        f = open(userDir + "/" + "default_" + str(count) + ".v", 'w', encoding='utf-8')
        f = open(os.path.join(userDir, test.topic+".v"), 'w', encoding='utf-8')
        f.write(upCode)  # 保存用户代码
        f.close()

        # 用于拷贝其他测试文件到当前次测试
        testFilePath = testFilesPath + fid + "/testFile/*"
        result, output = subprocess.getstatusoutput("cp -r " + testFilePath + " " + userDir)
        if result == 0:
            testState = "文件上传成功"
            state = "OK"

        currentPath = os.getcwd()
        os.chdir(userDir)  # 保存记录，但是由于路径问题，需要临时变换一下工作目录
        row = upList(test=test, grade=grade, state=testState,
                     user=user, upCode=upCode, info=info, count=count,
                     file_name="default_" + str(count) + ".v")
        os.chdir(currentPath)
        row.save()

        test.upNum += 1  # 题目提交数目 +1
        test.save()

        request.session['fid'] = fid
        request.session['count'] = count
        request.session['gradeAll'] = test.grade
        request.session['upTime'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

        logger.warning(request.session['user_name'] + " " + request.session['upTime'] + " file save over")

        data = {
            "state": state,
            "upTime": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
            "testState": testState,
            "recvCode": upCode,
            "info": info,
        }

        return HttpResponse(json.dumps(data), content_type='application/json')

    data = {"state": "ERROR", "testState": "未知错误，请联系管理员", "info": "非法请求"}
    return JsonResponse(data)


def startCompile(request):
    if request.method == "POST":
        if not os.path.exists(compileZipPath):
            os.makedirs(compileZipPath)
        if not os.path.exists(compileBitPath):
            os.makedirs(compileBitPath)
        if not os.path.exists(compileErrPath):
            os.makedirs(compileErrPath)

        global compileChecker
        if compileChecker is None:
            compileChecker = 1
            Timer(10, detectCompile).start()

        content = {
            'fid': request.session["fid"],
            'count': str(request.session["count"]),
            'userName': request.session['user_name'],
            'tempFilePath': compileZipPath + "ljw_test_{0}.zip".format(len(os.listdir(compileZipPath))),
            'topModuleName': testList.objects.get(id=request.session["fid"]).topModule,
        }

        utilities = ZipUtilities()
        path = os.path.join(userFilesPath, content['userName'], content['fid'], content['count'])
        filenames = os.listdir(path)
        for filename in filenames:
            filepath = os.path.join(path, filename)
            utilities.toZip(filepath, filename)
        z = utilities.zip_file

        z.write(content['tempFilePath'])
        with open(content['tempFilePath'], 'wb') as f:
            for data in z:
                f.write(data)
        print(content['userName'] + " " + request.session['upTime'] + " : zip over")

        global threadList
        global threadIndex
        if len(threadList) >= Compile_MAX_Thread:  # 表示当前没有编译线程资源
            data = {"state": "OK", "testState": "暂时没有编译线程资源，请稍后重新提交", "info": "Waiting"}
            return HttpResponse(json.dumps(data), content_type='application/json')

        content['threadIndex'] = str(threadIndex)  # 0
        threadList[content['threadIndex']] = CompileHandleThread(CompileThread(compileBit, content), TimeCounter())  # 0
        threadIndex += 1  # 1

        threadList[content['threadIndex']].start()
        print("compile start: " + content['threadIndex'])

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

        user = User2.objects.get(name=content['userName'])
        test = testList.objects.get(id=content['fid'])
        row = upList.objects.get(test=test, user=user, count=int(content['count']))
        row.state = "开启编译"
        row.info = "开始编译线程"
        row.save()

        data = {"state": "OK", "testState": "提交成功，接下来交给后台处理", "info": "start compile"}
        return HttpResponse(json.dumps(data), content_type='application/json')

    data = {"state": "ERROR", "testState": "非POST请求", "info": "启动编译失败"}
    return HttpResponse(json.dumps(data), content_type='application/json')


def detectCompile():
    global threadList

    global countCom
    if len(threadList) > 0 or countCom < 10:
        print("detect com " + str(len(threadList)))
        if len(threadList) == 0:
            countCom += 1
        else:
            countCom = 0

    startJudgeCount = 0
    startJudgeContent = []

    needToDel = []
    #global threadList
    for key in threadList:
        #print(key + ':' + threadList[key])
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

    #global judgeThreadList
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

# def detectCompile(request):
#     if request.method == "POST":
#         time = str(request.POST.get("time", -1))
#         fid = request.session["fid"]
#         count = request.session["count"]
#         user = User2.objects.get(name=request.session["user_name"])
#         test = testList.objects.get(id=fid)
#         row = upList.objects.get(test=test, user=user, count=request.session["count"])
#
#         print("compile " + str(time))
#
#         threadID = str(request.POST.get("threadID", None))
#         global threadList
#         if threadID == None or threadList[threadID] == None:
#             row.state = "编译失败"
#             row.info = "编译线程丢失"
#             row.save()
#             data = {"state": "ERROR", "info": "编译失败"}
#             return HttpResponse(json.dumps(data), content_type='application/json')
#
#         if threadList[threadID].get_result() is None:
#             if int(time) < Compile_MAX_Time:
#                 data = {"state": "OK", "compileState": "compiling...",
#                         "info": "编译进行中", "threadID": threadID,
#                         "time": time}
#                 return HttpResponse(json.dumps(data), content_type='application/json')
#             else:
#                 row.state = "编译时长超过"
#                 row.info = "编译超时"
#                 row.save()
#                 data = {"state": "ERROR", "compileState": "OVER", "testState": "编译超时", "info": "编译超时..."}
#                 return HttpResponse(json.dumps(data), content_type='application/json')
#         else:
#             # result = {'state': "OK", 'bitFilePath': "/tmp/bit/", 'bitFileName': "default_10.bit", 'info': "编译成功"}
#             print("编译完成")
#             result = threadList[threadID].get_result()
#             del threadList[threadID]
#
#             if result['state'] == 'OK':
#                 info = "编译完成"
#                 testState = "编译成功，准备测试"
#                 state = "OK"
#
#                 userDir = userFilesPath + request.session["user_name"] + "/" + fid + "/" + str(count)
#                 logger.warning(os.getcwd())
#                 res, output = subprocess.getstatusoutput(
#                     "cp " + os.path.join(result['bitFilePath'] + "/" + result['bitFileName']) + " " + userDir)
#
#                 row.comTime = int(time)
#
#                 if res == 0:
#                     row.state = testState
#                     row.info = info
#                     row.save()
#                     data = {
#                         "state": state,
#                         "testState": testState,
#                         "bitFileName": result['bitFileName'],
#                         "bitFilePath": userDir,
#                         'info': info,
#                         "compileState": "OVER",
#                     }
#                     return HttpResponse(json.dumps(data), content_type='application/json')
#
#                 row.state = "编译完成，数据拷贝出错"
#                 row.info = "bit文件数据拷贝出错"
#                 row.save()
#
#                 data = {"state": "ERROR", "compileState": "OVER", "testState": "数据拷贝出错", "info": "但是编译完成了"}
#                 return HttpResponse(json.dumps(data), content_type='application/json')
#
#             row.state = result['compileInfo']
#             row.info = "编译失败"
#             row.save()
#
#             data = {"state": "ERROR", "compileState": "OVER", "testState": result['compileInfo'], "info": "编译失败"}
#             return HttpResponse(json.dumps(data), content_type='application/json')
#
#     data = {"state": "ERROR", "testState": "非POST请求", "info": "编译失败"}
#     return HttpResponse(json.dumps(data), content_type='application/json')


# def startJudge(request):
#     if request.method == "POST":
#         bitFileName = request.POST.get("bitFileName", None)
#         bitFilePath = request.POST.get("bitFilePath", None)
#         fid = request.session["fid"]
#
#         content = {
#             'userName': request.session["user_name"],
#             'fid': request.session["fid"],
#             'count': request.session["count"],
#             'bitFileName': bitFileName
#         }
#
#         global threadID
#         global threadList
#         threadList[str(threadID)] = TestThread(exection, content)
#         currentThreadID = threadID
#         threadID += 1
#         threadList[str(currentThreadID)].start()
#         logger.warning("开始评测")
#
#         # result, cycle, testResult = 0, 999, [{'result': "答案正确", 'info': "测试 1"},
#         #                                     {'result': "答案正确", 'info': "测试 2"},
#         #                                     {'result': "答案正确", 'info': "测试 3"}]
#
#         data = {"state": "OK", "threadID": currentThreadID,
#                 "testingState": "testing...", "info": "开始评测"}
#         return HttpResponse(json.dumps(data), content_type='application/json')
#
#     data = {"state": "ERROR", "testState": "非POST请求", "info": "启动评测失败"}
#     return HttpResponse(json.dumps(data), content_type='application/json')


# def detectJudge(request):
#     if request.method == "POST":
#         fid = request.session["fid"]
#         user = User2.objects.get(name=request.session["user_name"])
#         test = testList.objects.get(id=fid)
#         row = upList.objects.get(test=test, user=user, count=request.session["count"])
#         time = str(request.POST.get("time", -1))
#
#         print("judge " + str(time))
#
#         threadID = str(request.POST.get("threadID", None))
#         global threadList
#         if threadID == None or threadList[threadID] == None:
#             row.state = "测试失败"
#             row.info = "测试线程丢失"
#             row.save()
#             data = {"state": "ERROR", "info": "测试失败"}
#             return HttpResponse(json.dumps(data), content_type='application/json')
#
#         if threadList[threadID].get_result() is None:
#             if int(time) < Test_MAX_Time:
#                 data = {"state": "OK", "testingState": "testing...",
#                         "info": "测试进行中", "threadID": threadID,
#                         "time": time}
#                 return HttpResponse(json.dumps(data), content_type='application/json')
#             else:
#                 row.state = "测试超时"
#                 row.info = "测试超时"
#                 row.save()
#                 data = {
#                     "info": "测试超时",
#                     "testState": "测试超时",
#                     "testingState": "OVER",
#                 }
#                 return HttpResponse(json.dumps(data), content_type='application/json')
#         else:
#             result, cycle, testResult = threadList[threadID].get_result()
#
#             row.exeTime = int(time)
#
#             if result == 0:
#                 state = "OK"
#                 info = testResult
#                 testState = "测试流程执行完成"
#                 cnt = 0
#                 for res in testResult:
#                     if res['result'] == "答案正确":
#                         cnt = cnt + 1
#                 grade = round(cnt / len(testResult) * test.grade, 2)
#                 judge = "尝试"
#                 if cnt == len(testResult):
#                     judge = "通过"
#             else:
#                 state = "ERROR"
#                 info = "未知错误"
#                 testState = "测试流程失败（测试超时，请检查代码）"
#                 grade = 0.00
#                 judge = "尝试"
#
#             row.state = testState
#             row.info = info
#             row.grade = grade
#             row.judge = judge
#             row.cycle = cycle
#             row.save()
#
#             if judge == "通过":
#                 test.passNum += 1  # 测试通过数目 +1
#                 test.save()
#                 # 修改，通过条件下用时最少的代码
#                 passRecords = passList.objects.filter(test=test, user=user)
#                 if len(passRecords) == 0:
#                     passRecord = passList()
#                     passRecord.user = user
#                     passRecord.test = test
#                     passRecord.grade = grade
#                     # passRecord.passTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
#                     passRecord.leastCycle = cycle
#                     passRecord.passCode = row.upCode
#                     passRecord.info = row.info
#                     passRecord.save()
#                 elif cycle < passRecords[0].leastCycle:
#                     # passRecords[0].passTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
#                     passRecords[0].leastCycle = cycle
#                     passRecords[0].passCode = row.upCode
#                     passRecords[0].info = row.info
#                     passRecords[0].save()
#
#             if grade > 0.0:
#                 # 修改有得分的提交里，最高得分的情况
#                 gradeRecords = gradeList.objects.filter(test=test, user=user)
#                 if len(gradeRecords) == 0:
#                     gradeMax = gradeList()
#                     gradeMax.user = user
#                     gradeMax.test = test
#                     gradeMax.maxGrade = grade
#                     gradeMax.passCode = row.upCode
#                     gradeMax.info = row.info
#                     gradeMax.save()
#                 elif grade > gradeRecords[0].maxGrade:
#                     gradeRecords[0].maxGrade = grade
#                     gradeRecords[0].passCode = row.upCode
#                     gradeRecords[0].info = row.info
#                     gradeRecords[0].save()
#
#             logger.warning("评测结束！")
#
#             data = {
#                 "state": state,
#                 "testState": testState,
#                 "testResult": testResult,
#                 "grade": grade,
#                 "testingState": "OVER",
#             }
#             return HttpResponse(json.dumps(data), content_type='application/json')
#
#     data = {"state": "ERROR", "testState": "未知错误", "info": "非POST请求"}
#     return HttpResponse(json.dumps(data), content_type='application/json')


def download(request):
    userName = request.GET.get('userName')
    fid = request.GET.get('fid')
    count = request.GET.get('count')
    bitFileName = request.GET.get('bitFileName')
    deviceId = request.GET.get('deviceId')
    logger.warning(userName + " " + fid + " " + count + " " + bitFileName + " " + deviceId)

    file = open(userFilesPath + userName + "/" + fid + "/" + count + "/" + bitFileName, 'rb')
    response = HttpResponse(file)
    response['Content-Type'] = 'application/octet-stream'  # 设置头信息，告诉浏览器这是个文件
    response['Content-Disposition'] = 'attachment;filename="{0}.bit"'.format(deviceId)
    return response


def submission(request, user_name):
    submissionList = []
    if user_name:
        allSubmissionList = upList.objects.filter(
            user=User2.objects.get(name=user_name)).order_by('-upTime')[:20]
        for p in allSubmissionList:
            submissionList.append({"user": user_name, "title": p.test.title,
                                   "upTime": p.upTime, "judge": p.judge,
                                   "state": p.state, "grade": p.grade,
                                   "cycle": p.cycle, "upId": p.id})

    content = {
        'submissionList': submissionList,
        'type': "SINGLE"
    }
    return render(request, "Test/submission.html", content)


def submissionAll(request):
    submissionList = []
    allSubmissionList = upList.objects.all().order_by('-upTime')[:50]
    for p in allSubmissionList:
        submissionList.append({"user": p.user.name, "title": p.test.title,
                               "upTime": p.upTime, "judge": p.judge,
                               "state": p.state, "grade": p.grade,
                               "cycle": p.cycle, "upId": p.id})

    content = {
        'submissionList': submissionList,
        'type': "ALL"
    }
    return render(request, "Test/submission.html", content)


def seeCode(request, upId):
    code = upList.objects.get(id=upId).upCode
    return HttpResponse(code, content_type="text/plain; charset=utf-8")


def seeInfo(request, upId):
    info = upList.objects.get(id=upId).info
    return HttpResponse(info, content_type="text/plain; charset=utf-8")


def passRec(request, user_name):
    passRecList = []
    if user_name:
        allPassList = passList.objects.filter(
            user=User2.objects.get(name=user_name)).order_by("test")
        for p in allPassList:
            passRecList.append({"user": p.user.name, "title": p.test.title,
                                "passTime": p.passTime, "cycle": p.leastCycle,
                                "passId": p.id, "grade": p.grade})

    content = {
        'passList': passRecList,
        'type': "SINGLE"
    }
    return render(request, "Test/passRecord.html", content)


def passRecAll(request):
    passRecList = []
    allPassList = passList.objects.all().order_by("test")
    for p in allPassList:
        passRecList.append({"user": p.user.name, "title": p.test.title,
                            "passTime": p.passTime, "cycle": p.leastCycle,
                            "passId": p.id, "grade": p.grade})

    content = {
        'passList': passRecList,
        'type': "ALL"
    }
    return render(request, "Test/passRecord.html", content)


def seeCodePass(request, passId):
    code = passList.objects.get(id=passId).passCode
    return HttpResponse(code, content_type="text/plain; charset=utf-8")


def seeInfoPass(request, passId):
    info = passList.objects.get(id=passId).info
    return HttpResponse(info, content_type="text/plain; charset=utf-8")


def ranking(request):
    gradeLists = gradeList.objects.all().values('user__name'). \
        annotate(Sum("maxGrade"), Count("user__name"), Max("upTime")).order_by("user__name")
    passLists = passList.objects.all().values('user__name'). \
        annotate(Sum("grade"), Count("user__name"), Max("passTime")).order_by("user__name")
    persons = User2.objects.all().values("name").order_by("name")

    print(gradeLists)
    print(passLists)
    print(persons)

    rankings = []

    g = 0
    p = 0
    for r in persons:
        if g < len(gradeLists) and r["name"] == gradeLists[g]["user__name"] and \
                p < len(passLists) and r["name"] == passLists[p]["user__name"]:
            rankings.append({"user": r["name"],
                             "passN": passLists[p]["user__name__count"],
                             "passG": passLists[p]["grade__sum"],
                             "passT": passLists[p]["passTime__max"],
                             "allN": gradeLists[g]["user__name__count"],
                             "allG": gradeLists[g]["maxGrade__sum"],
                             "allT": gradeLists[g]["upTime__max"]})
            p += 1
            g += 1
        elif g < len(gradeLists) and r["name"] == gradeLists[g]["user__name"]:
            rankings.append({"user": r["name"],
                             "passN": 0,
                             "passG": 0.00,
                             "passT": "~~",
                             "allN": gradeLists[g]["user__name__count"],
                             "allG": gradeLists[g]["maxGrade__sum"],
                             "allT": gradeLists[g]["upTime__max"]})
            g += 1
        elif p < len(passLists) and r["name"] == passLists[p]["user__name"]:
            rankings.append({"user": r["name"],
                             "passN": passLists[p]["user__name__count"],
                             "passG": passLists[p]["grade__sum"],
                             "passT": passLists[p]["passTime__max"],
                             "allN": 0,
                             "allG": 0.00,
                             "allT": "~~"})
            p += 1
        else:
            rankings.append({"user": r["name"],
                             "passN": 0,
                             "passG": 0.00,
                             "passT": "~~",
                             "allN": 0,
                             "allG": 0.00,
                             "allT": "~~"})

    print(rankings)

    rankings.sort(key=lambda x: (-x["passN"], -x["passG"],
                                 -x["allN"], -x["allG"], x["passT"], x["allT"]))

    content = {
        'rankings': rankings,
        'type': "ALL"
    }
    return render(request, "Test/rankList.html", content)


def guide(request):
    file = open("static/testGuide.md", 'r', encoding='utf-8')
    guideFile = file.read()
    file.close()

    content = {
        "guideFile": guideFile,
    }

    return render(request, "Test/testGuide.html", content)

#  备份测试运行函数
# def judgeMent(request):
#     if request.method == "POST":
#         bitFileName = request.POST.get("bitFileName", None)
#         bitFilePath = request.POST.get("bitFilePath", None)
#         fid = request.session["fid"]
#
#         content = {
#             'userName': request.session["user_name"],
#             'fid': request.session["fid"],
#             'count': request.session["count"],
#             'bitFileName': bitFileName
#         }
#
#         logger.warning("开始评测")
#         result, cycle, testResult = exection(content)
#         #result, cycle, testResult = 0, 999, [{'result': "答案正确", 'info': "测试 1"},
#         #                                     {'result': "答案正确", 'info': "测试 2"},
#         #                                     {'result': "答案正确", 'info': "测试 3"}]
#
#         user = User2.objects.get(name=request.session["user_name"])
#         test = testList.objects.get(id=fid)
#
#         if result == 0:
#             state = "OK"
#             info = testResult
#             testState = "测试流程执行完成"
#             cnt = 0
#             for res in testResult:
#                 if res['result'] == "答案正确":
#                     cnt = cnt+1
#             grade = round(cnt/len(testResult)*test.grade, 2)
#             judge = "尝试"
#             if cnt == len(testResult):
#                 judge = "通过"
#             # cycle = 999
#         else:
#             state = "ERROR"
#             info = "未知错误"
#             testState = "测试流程失败"
#             grade = 0.00
#             judge = "尝试"
#             # cycle = -1
#
#         row = upList.objects.get(test=test, user=user, count=request.session["count"])
#         row.state = testState
#         row.info = info
#         row.grade = grade
#         row.judge = judge
#         row.cycle = cycle
#         row.save()
#
#         if judge == "通过":
#             test.passNum += 1  # 测试通过数目 +1
#             test.save()
#             # 修改，通过条件下用时最少的代码
#             passRecords = passList.objects.filter(test=test, user=user)
#             if len(passRecords) == 0:
#                 passRecord = passList()
#                 passRecord.user = user
#                 passRecord.test = test
#                 passRecord.grade = grade
#                 # passRecord.passTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
#                 passRecord.leastCycle = cycle
#                 passRecord.passCode = row.upCode
#                 passRecord.info = row.info
#                 passRecord.save()
#             elif cycle < passRecords[0].leastCycle:
#                 # passRecords[0].passTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
#                 passRecords[0].leastCycle = cycle
#                 passRecords[0].passCode = row.upCode
#                 passRecords[0].info = row.info
#                 passRecords[0].save()
#
#         if grade > 0.0:
#             # 修改有得分的提交里，最高得分的情况
#             gradeRecords = gradeList.objects.filter(test=test, user=user)
#             if len(gradeRecords) == 0:
#                 gradeMax = gradeList()
#                 gradeMax.user = user
#                 gradeMax.test = test
#                 gradeMax.maxGrade = grade
#                 gradeMax.passCode = row.upCode
#                 gradeMax.info = row.info
#                 gradeMax.save()
#             elif grade > gradeRecords[0].maxGrade:
#                 gradeRecords[0].maxGrade = grade
#                 gradeRecords[0].passCode = row.upCode
#                 gradeRecords[0].info = row.info
#                 gradeRecords[0].save()
#
#
#         # logger.warning("评测结束 " + str(info))
#         logger.warning("评测结束！")
#
#         data = {
#             "state": state,
#             "testState": testState,
#             "testResult": testResult,
#             "grade": grade
#         }
#         return HttpResponse(json.dumps(data), content_type='application/json')
#
#     data = {"state": "ERROR", "testState": "未知错误", "info": "非POST请求"}
#     return HttpResponse(json.dumps(data), content_type='application/json')

#  编译函数备份
# def startCompile(request):
#     if request.method == "POST":
#         if not os.path.exists(compileZipPath):
#             os.makedirs(compileZipPath)
#         if not os.path.exists(compileBitPath):
#             os.makedirs(compileBitPath)
#         if not os.path.exists(compileErrPath):
#             os.makedirs(compileErrPath)
#
#         fid = request.session["fid"]
#         count = request.session["count"]
#         tempFilePath = compileZipPath + "ljw_test_{0}.zip".format(len(os.listdir(compileZipPath)))
#
#         utilities = ZipUtilities()
#         path = os.path.join(userFilesPath, request.session['user_name'], fid, str(count))
#         filenames = os.listdir(path)
#         for filename in filenames:
#             filepath = os.path.join(path, filename)
#             utilities.toZip(filepath, filename)
#         z = utilities.zip_file
#
#         z.write(tempFilePath)
#         with open(tempFilePath, 'wb') as f:
#             for data in z:
#                 f.write(data)
#         print(request.session['user_name'] + " " + request.session['upTime'] + " : zip over")
#
#         #result = compileBit(tempFilePath, testList.objects.get(id=fid).topModule)
#         result = {'state': "OK", 'bitFilePath': "/tmp/bit/", 'bitFileName': "default_10.bit", 'info': "编译成功"}
#         print(result)
#         logger.warning("编译信息：")
#
#         if result['state'] == 'OK':
#             info = "编译完成"
#             testState = "编译成功，正在测试"
#             state = "OK"
#
#             userDir = userFilesPath + request.session["user_name"] + "/" + fid + "/" + str(count)
#             logger.warning(os.getcwd())
#             res, output = subprocess.getstatusoutput(
#                 "cp " + os.path.join(result['bitFilePath'] + "/" + result['bitFileName']) + " " + userDir)
#
#             if res == 0:
#                 user = User2.objects.get(name=request.session["user_name"])
#                 test = testList.objects.get(id=fid)
#                 row = upList.objects.get(test=test, user=user, count=request.session["count"])
#                 row.state = testState
#                 row.info = info
#                 row.save()
#                 data = {
#                     "state": state,
#                     "testState": testState,
#                     "bitFileName": result['bitFileName'],
#                     "bitFilePath": userDir,
#                     'info': info
#                 }
#                 return HttpResponse(json.dumps(data), content_type='application/json')
#
#             data = {"state": "ERROR", "testState": "数据拷贝出错", "info": "编译失败"}
#             return HttpResponse(json.dumps(data), content_type='application/json')
#
#         data = {"state": "ERROR", "testState": result['compileInfo'], "info": "编译失败"}
#         return HttpResponse(json.dumps(data), content_type='application/json')
#
#     data = {"state": "ERROR", "testState": "非POST请求", "info": "编译失败"}
#     return HttpResponse(json.dumps(data), content_type='application/json')
