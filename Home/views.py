import os, json, time
# import struct
# import numpy as np
from django.core.files import File
from django.db.models import Sum, Count, Max
from django.http import HttpResponse, JsonResponse, FileResponse
from django.shortcuts import render, redirect
from Constant import constants as const
from Login.models import User
from Home import forms
from Home.models import *
from FrexTTest.settings import userFilesPath, compileErrPath, testFilesPath, compileZipPath, compileBitPath, \
    Compile_MAX_Thread, Compile_MAX_Time, Judge_MAX_Time
from FileHandler import file_request as fh

import logging

logger = logging.getLogger(__name__)

# Create your views here.


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


# def read_file():  # 函数功能为：将一个文件夹下所有二进制文件以每四个字节方式读取，将读取出的数据转换为浮点类型的数据并以txt格式保存到新的地址去
#     path = './二进制文件所在文件夹名称'  # 文件夹地址
#     new_path = './要存放生成txt文件的文件夹名称/'  # 新的存放生成文件的文件夹地址
#     b_list = ['此处填写二进制文件名称（也可以参考2020.11.10所写博客，利用后缀名找到path文件夹下所有二进制文件）']
#
#     for b_file in b_list:
#         f = open(path + '/' + b_file, 'rb')  # 对b_list列表的文件以二进制方式读取
#         b_file_ext = os.path.splitext(b_file)  # 分离二进制文件前后缀，b_front为前缀名，b_ext为后缀名
#         b_front, b_ext = b_file_ext
#         m = []  # 空列表用于存放二进制数据转换为的浮点数
#         while True:  # 每四个字节进行读取以及格式转换
#             a = f.read(4)
#             if a == b'':  # 为空结束循环
#                 break
#             a_float = struct.unpack("f", a)[0]  # 此处存在存储的大小端问题   将二进制数据转换为浮点数
#             m.append(a_float)
#         m_array = np.array(m)  # 将m列表转换为array数组
#         if not os.path.exists(new_path):  # 判断工作目录有无new_path文件夹，若无则创建
#             os.mkdir(new_path)
#         np.savetxt(new_path + b_front + '.txt', m_array)  # 对文件进行重命名并保存到新的文件夹
#         f.close()

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
    return render(request, "TestHome/testList.html", content)


def test_page(request, t_uid):
    test = TestList.objects.get(uid=t_uid)

    # file = open(testFilesPath + str(t_uid) + "/" +
    #             test.topic + ".md", 'r', encoding="utf-8")
    # testFile = file.read()
    # file.close()

    content = {
        "testFile": test.content,
        "type": test.type,
        "title": test.title,
        "author": test.author,
        "company": test.company,
        "t_uid": test.uid,
        "grade": test.grade,
    }

    return render(request, "TestHome/testPage.html", content)


def show_last(request):
    if request.method == "POST":
        t_uid = request.POST.get("t_uid", None)
        test = TestList.objects.get(uid=t_uid)
        user = User.objects.get(uid=request.session["u_uid"])
        upRecords = SubmitList.objects.filter(test=test, user=user).order_by("submit_time")

        upRecord = upRecords.last()
        data = {"state": "OK", "upTime": upRecord.submit_time, "testState": upRecord.status,
                "recvCode": upRecord.code, "testGrade": upRecord.score}
        if upRecord.result:
            data["testResult"] = json.loads(upRecord.result)

        return JsonResponse(data)
    data = {"state": "ERROR", "testState": "未知错误，请联系管理员", "info": "非法请求"}
    return JsonResponse(data)


def add_test(request):
    if request.method == "POST":
        if request.session['is_login'] and request.session['role'] == 'admin':
            newTest_form = forms.NewTestForm(request.POST, request.FILES)
            # print(newTest_form)
            # print(newTest_form.is_valid())
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
                        with open(os.path.join(testFilesPath, str(test.uid), test.topic+".md"), "r", encoding='utf-8') as f:
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
                test = TestList.objects.get(uid=values.get('topic'))  # NOTE: topic = uid
                files = request.FILES.getlist('files')

                ff = TestFile()
                for f in files:
                    ff.test = test
                    ff.file_path = os.path.join(test.file_path, f.__str__())
                    handle_uploaded_file(ff.file_path, f)
                    with open(ff.file_path, "rb") as tf:
                        ff.content = tf.read()
                    ff.save()
                    break  # NOTE: only one file is permitted

                with open(ff.file_path, 'rb') as f:
                    if fh.post_questions({
                        const.c_testId: str(test.uid),
                        const.c_topic: str(test.topic),
                    }, f) == const.request_failed:
                        message = '提交失败'
                        return render(request, "TestHome/addTestFile.html", locals())

                message = '提交成功'
                return render(request, "TestHome/addTestFile.html", locals())
            else:
                errors = addTestFile_form.errors
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
        t_uid = request.POST.get("t_uid", None)
        code = request.POST.get("testUserCode", None)

        test = TestList.objects.get(uid=t_uid)
        user = User.objects.get(uid=request.session["u_uid"])

        row = SubmitList(test=test, user=user)
        row.save()      # generate uid

        userDir = os.path.join(userFilesPath, "user", str(user.uid),
                               "testing", str(t_uid), str(row.uid))
        if not os.path.exists(userDir):  # 如果用户首次提交这个题目的代码，那么创建目录
            os.makedirs(userDir)
        f = open(os.path.join(userDir, test.topic+".v"), 'wt')
        f.write(code)  # 保存用户代码
        f.close()

        with open(os.path.join(userDir, test.topic+".v"), 'rt') as f:
            if fh.post_test({
                const.c_userId: str(user.uid),
                const.c_testId: str(test.uid),
                const.c_submitId: str(row.uid),
                const.c_topic: test.topic,
            }, f) == const.request_success:
                row.state = state_try
                row.code = code
                row.status = "代码提交成功"
                row.message = str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())) + " Success: code submit complete.\n"
                row.save()
            else:
                row.code = code
                row.status = "代码提交失败"
                row.message = str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())) + " Failed: code submit complete.\n"
                row.save()

        test.submit_number += 1  # 题目提交数目 +1
        test.save()

        request.session['t_uid'] = str(t_uid)
        request.session['s_uid'] = str(row.uid)
        request.session['upTime'] = row.submit_time.__str__()

        state = "OK"
        data = {
            "state": state,
            "upTime": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
            "testState": row.status,
            "recvCode": code,
            "info": row.message,
        }
        return HttpResponse(json.dumps(data), content_type='application/json')

    data = {"state": "ERROR", "testState": "未知错误，请联系管理员", "info": "非法请求"}
    return JsonResponse(data)


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
    # response["Content-Disposition"] = "attachment; filename*=UTF-8''{}".format(escape_uri_path(filename)) # 中文文件名
    return response


# check u_uid
def get_submission(request, u_uid):
    submissionList = []
    if u_uid:
        allSubmissionList = SubmitList.objects.filter(
            user=User.objects.get(uid=u_uid)).order_by('-submit_time')[:20]
        for p in allSubmissionList:
            submissionList.append({"user": p.user.name, "title": p.test.title,
                                   "upTime": p.submit_time, "judge": p.state,
                                   "state": p.status, "grade": p.score,
                                   "cycle": p.cycle, "upId": p.uid,
                                   "luts": p.lut_count, "ffs": p.ff_count})

    content = {
        'submissionList': submissionList,
        'type': "SINGLE"
    }
    return render(request, "TestHome/submission.html", content)


def submission_all(request):
    submissionList = []
    allSubmissionList = SubmitList.objects.all().order_by('-submit_time')[:50]
    for p in allSubmissionList:
        submissionList.append({"user": p.user.name, "title": p.test.title,
                               "upTime": p.submit_time, "judge": p.state,
                               "state": p.status, "grade": p.score,
                               "cycle": p.cycle, "upId": p.uid,
                               "luts": p.lut_count, "ffs": p.ff_count})

    content = {
        'submissionList': submissionList,
        'type': "ALL"
    }
    return render(request, "TestHome/submission.html", content)


def see_code(request, upId):
    code = SubmitList.objects.get(uid=upId).code
    return HttpResponse(code, content_type="text/plain; charset=utf-8")


def see_info(request, upId):
    info = SubmitList.objects.get(uid=upId).message
    return HttpResponse(info, content_type="text/plain; charset=utf-8")


def see_result(request, upId):
    results = SubmitList.objects.filter(uid=upId)
    if len(results) > 0 and results[0].result:
        result = json.loads(results[0].result)
    else:
        result = "not ready please see later."
    return HttpResponse(result, content_type="text/plain; charset=utf-8")


def pass_record(request, u_uid):
    passRecList = []
    if u_uid:
        allPassList = ValidSubmitList.objects.filter(
            user=User.objects.get(uid=u_uid)).order_by("test")
        for p in allPassList:
            passRecList.append({"user": p.user.name, "title": p.test.title,
                                "passTime": p.submit.submit_time, "cycle": p.submit.cycle,
                                "passId": p.uid, "grade": p.submit.score})

    content = {
        'passList': passRecList,
        'type': "SINGLE"
    }
    return render(request, "TestHome/passRecord.html", content)


def pass_record_all(request):
    passRecList = []
    allPassList = ValidSubmitList.objects.all().order_by("test")
    for p in allPassList:
        passRecList.append({"user": p.user.name, "title": p.test.title,
                            "passTime": p.submit.submit_time, "cycle": p.submit.cycle,
                            "passId": p.uid, "grade": p.submit.score})

    content = {
        'passList': passRecList,
        'type': "ALL"
    }
    return render(request, "TestHome/passRecord.html", content)


def see_code_valid(request, passId):
    code = ValidSubmitList.objects.get(uid=passId).submit.code
    return HttpResponse(code, content_type="text/plain; charset=utf-8")


def see_info_valid(request, passId):
    info = ValidSubmitList.objects.get(uid=passId).submit.message
    return HttpResponse(info, content_type="text/plain; charset=utf-8")


def ranking(request):
    gradeLists = BestSubmitList.objects.all().values('user__name'). \
        annotate(Sum("submit__score"), Count("user__name"), Max("submit__submit_time")).order_by("user__name")
    passLists = ValidSubmitList.objects.all().values('user__name'). \
        annotate(Sum("submit__score"), Count("user__name"), Max("submit__submit_time")).order_by("user__name")
    persons = User.objects.all().values("name").order_by("name")

    # print(gradeLists)
    # print(passLists)
    # print(persons)

    rankings = []

    g = 0
    p = 0
    for r in persons:
        if g < len(gradeLists) and r["name"] == gradeLists[g]["user__name"] and \
                p < len(passLists) and r["name"] == passLists[p]["user__name"]:
            rankings.append({"user": r["name"],
                             "passN": passLists[p]["user__name__count"],
                             "passG": passLists[p]["submit__score__sum"],
                             "passT": passLists[p]["submit__submit_time__max"],
                             "allN": gradeLists[g]["user__name__count"],
                             "allG": gradeLists[g]["submit__score__sum"],
                             "allT": gradeLists[g]["submit__submit_time__max"]})
            p += 1
            g += 1
        elif g < len(gradeLists) and r["name"] == gradeLists[g]["user__name"]:
            rankings.append({"user": r["name"],
                             "passN": 0,
                             "passG": 0.00,
                             "passT": "~~",
                             "allN": gradeLists[g]["user__name__count"],
                             "allG": gradeLists[g]["submit__score__sum"],
                             "allT": gradeLists[g]["submit__submit_time__max"]})
            g += 1
        elif p < len(passLists) and r["name"] == passLists[p]["user__name"]:
            rankings.append({"user": r["name"],
                             "passN": passLists[p]["user__name__count"],
                             "passG": passLists[p]["submit__score__sum"],
                             "passT": passLists[p]["submit__submit_time__max"],
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

    # print(rankings)

    rankings.sort(key=lambda x: (-x["passN"], -x["passG"],
                                 -x["allN"], -x["allG"], x["passT"], x["allT"]))

    content = {
        'rankings': rankings,
        'type': "ALL"
    }
    return render(request, "TestHome/rankList.html", content)


def guide(request):
    file = open("static/testGuide.md", 'r', encoding='utf-8')
    guideFile = file.read()
    file.close()

    content = {
        "guideFile": guideFile,
    }

    return render(request, "TestHome/testGuide.html", content)
