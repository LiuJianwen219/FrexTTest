from django.conf.urls import url
from django.urls import path

from Suggestion import views

urlpatterns = [
    path('addSuggestion/', views.add_suggestion),
    path('', views.suggestions),
]