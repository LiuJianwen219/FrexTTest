from django.conf.urls import url
from django.urls import path, include

from Admin import views

urlpatterns = [
    path('', views.dashboard),
]
