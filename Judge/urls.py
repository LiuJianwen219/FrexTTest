from django.conf.urls import url
from django.urls import path

from Judge import views

urlpatterns = [
    path('startJudge/', views.start_judge),
    path('judge_result/', views.judge_result),
]
