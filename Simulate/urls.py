from django.conf.urls import url
from django.urls import path

from Simulate import views

urlpatterns = [
    path("simulations/", views.simulations),
    path("simulate_code/", views.simulate_code),
]
