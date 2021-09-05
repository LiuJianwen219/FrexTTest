from django.conf.urls import url
from django.urls import path, include

from Login import views

urlpatterns = [
    path('', views.login),
    path('register/', views.register),
    path('logout/', views.logout),
    path('findPasswd/', views.find_password),
    url(r'^captcha/', include('captcha.urls')),
]
