from django.conf.urls import url
from django.urls import path, include

from Admin import views

urlpatterns = [
    path('add_resource/', views.add_thread_resource),
    path('', views.dashboard),
]
