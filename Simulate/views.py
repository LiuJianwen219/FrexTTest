import json

import requests
from django.http import HttpResponse
from django.shortcuts import render, redirect

# Create your views here.
from FrexTTest.settings import Simulate_Server_Url, Simulate_Server_Api
from Home.models import TestList
from Home.views import access_check_record, response_ok, response_error
from Login.models import User
from Simulate.models import SimulateRecord, type_sim, state_success


def simulations(request):
    if 'is_login' not in request.session:
        return redirect("/")

    if not request.session['u_uid']:
        return redirect('/login/')

    if request.method == "POST":
        t_uid = request.POST.get("t_uid", None)
        sim_type = request.POST.get("sim_type", "save")
        code = request.POST.get("testUserCode", None)
        sim_code = request.POST.get("testUserSimCode", None)

        test = TestList.objects.get(uid=t_uid)
        user = User.objects.get(uid=request.session["u_uid"])

        sim_record = SimulateRecord(user=user, test=test, code=code, sim_code=sim_code)

        if sim_type == "simulate":
            sim_record.type = type_sim
            access_check_record(request, "simulation", "仿真")
            data = {
                "testbench": sim_code,
                "verilog": code,
                "runtime": 50,  # 运行时长，为空则运行50个时钟单位
                "monitorList": [],  # 待观察信号名列表，为空则默认观察testbench文件中的所有信号
            }

            response = requests.post(Simulate_Server_Url + Simulate_Server_Api, data=json.dumps(data))
            sim_record.sim_result = response.content
            data = json.loads(response.content)
            if data['msg'] == "success":
                sim_record.sim_result_url = data['data']['html']
                sim_record.state = state_success
                r_data = response_ok()
                r_data['sim_result_html'] = data['data']['html']
            else:
                r_data = response_error(data['msg'])
            sim_record.save()
            return HttpResponse(json.dumps(r_data), content_type='application/json')

        access_check_record(request, "simulation", "保存仿真代码")
        sim_record.state = state_success
        sim_record.save()
        return HttpResponse(json.dumps(response_ok()), content_type='application/json')

    return HttpResponse(json.dumps(response_error("非法访问")), content_type='application/json')


def simulate_code(request):
    if 'is_login' not in request.session:
        return redirect("/")

    if not request.session['u_uid']:
        return redirect('/login/')

    if request.method == "POST":
        t_uid = request.POST.get('t_uid', None)
        sim_record = SimulateRecord.objects.filter(user__uid=request.session["u_uid"],
                                                   test__uid=t_uid).order_by('-create_time')
        if len(sim_record) == 0:
            return HttpResponse(json.dumps(response_error("没有记录")), content_type='application/json')

        r_data = response_ok()
        r_data["sim_code"] = sim_record[0].sim_code
        return HttpResponse(json.dumps(r_data), content_type='application/json')

    return HttpResponse(json.dumps(response_error("非法访问")), content_type='application/json')
