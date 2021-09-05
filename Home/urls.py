from django.conf.urls import url
from django.urls import path

from Home import views

urlpatterns = [
    path("", views.test_introduce),

    path('testList/', views.test_list),
    url(r'testPage/(?P<fid>([0-9a-zA-Z_-]+))/$', views.test_page),

    path('upCode/', views.upCode),
    path('startCompile/', views.startCompile),
    path('showLast/', views.show_last),
    # path('detectCompile/', views.detectCompile),
    # path('startJudge/', views.startJudge),
    # path('detectJudge/', views.detectJudge),

    path('guide/', views.guide),
    path('resource/', views.building),

    path('addTest/', views.add_test),
    path('addTestFile/', views.add_test_file),

    path('submissionAll/', views.submissionAll),
    url(r'submission/(?P<user_name>(.+))/$', views.submission),
    url(r'seeCode/(?P<upId>([0-9]+))/$', views.seeCode),
    url(r'seeInfo/(?P<upId>([0-9]+))/$', views.seeInfo),

    path('passRecAll/', views.passRecAll),
    url(r'passRec/(?P<user_name>(.+))/$', views.passRec),
    url(r'seeCodePass/(?P<passId>([0-9]+))/$', views.seeCodePass),
    url(r'seeInfoPass/(?P<passId>([0-9]+))/$', views.seeInfoPass),

    url(r'download/$', views.download),

    path('ranking/', views.ranking),
    path('enterExotic/', views.enter_exotic),

]
