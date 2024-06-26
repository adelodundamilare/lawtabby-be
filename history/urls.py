from django.urls import path
from . import views

urlpatterns = [
    path('latest/', views.latest, name='history_latest'),
    path('all/', views.all, name='history_all'),
    path('user_uploads/', views.user_uploads, name='history_user_uploads'),
    path('user_downloads/', views.user_downloads, name='history_user_uploads'),
]