from django.conf.urls import url
from django.urls import path

from Compile import views

urlpatterns = [
    path('startCompile/', views.start_compile),
    path('compile_result/', views.compile_result),
    # path('detectCompile/', views.detect_compile),
    # path('startJudge/', views.startJudge),
    # path('detectJudge/', views.detectJudge),
]
