from django.urls import path
from . import views

urlpatterns = [
    path('latest/', views.latest, name='history_latest'),
    path('all/', views.all, name='history_all'),
]