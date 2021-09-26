from django.conf.urls import url
from django.urls import path

from Home import views

urlpatterns = [
    path("", views.test_introduce),

    path('testList/', views.test_list),
    url(r'testPage/(?P<t_uid>([0-9a-zA-Z_-]+))/$', views.test_page),

    path('upCode/', views.submit_code),
    # path('startCompile/', views.start_compile),
    path('showLast/', views.show_last),
    # path('detectCompile/', views.detectCompile),
    # path('startJudge/', views.startJudge),
    # path('detectJudge/', views.detectJudge),

    path('guide/', views.guide),
    path('resource/', views.building),

    path('addTest/', views.add_test),
    path('addTestFile/', views.add_test_file),

    path('submissionAll/', views.submission_all),
    url(r'submission/(?P<u_uid>(.+))/$', views.get_submission),
    url(r'seeCode/(?P<upId>(.+))/$', views.see_code),
    url(r'seeInfo/(?P<upId>(.+))/$', views.see_info),
    url(r'seeResult/(?P<upId>(.+))/$', views.see_result),

    path('passRecAll/', views.pass_record_all),
    url(r'passRec/(?P<u_uid>(.+))/$', views.pass_record),
    url(r'seeCodePass/(?P<passId>(.+))/$', views.see_code_valid),
    url(r'seeInfoPass/(?P<passId>(.+))/$', views.see_info_valid),

    url(r'download/$', views.download),

    path('ranking/', views.ranking),
    path('enterExotic/', views.enter_exotic),

]
