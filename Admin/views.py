import json

from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
from Compile.views import get_max_compile_thread, get_compiling_thread, add_compile_thread_resource
from Home.views import response_ok


def dashboard(request):
    content = {
        "maxCompile": get_max_compile_thread(),
        "compiling": get_compiling_thread(),
    }
    return render(request, "Admin/dashboard.html", content)


def add_thread_resource(request):
    add_compile_thread_resource()
    return HttpResponse(json.dumps(response_ok()), content_type='application/json')
