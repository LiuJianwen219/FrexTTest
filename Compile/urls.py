from django.conf.urls import url
from django.urls import path

from Home import views

urlpatterns = [
    path("", views.test_introduce),
    path('startCompile/', views.startCompile),
    # path('detectCompile/', views.detectCompile),
    # path('startJudge/', views.startJudge),
    # path('detectJudge/', views.detectJudge),
]
