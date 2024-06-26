from django.urls import path
from . import views

urlpatterns = [
    path('latest/', views.latest, name='history_latest'),
    path('all/', views.all, name='history_all'),
    path('user_uploads/', views.user_uploads, name='history_user_uploads'),
    path('rename_upload/', views.rename_upload, name='history_rename_upload'),
    path('delete_upload/<int:id>/', views.delete_upload, name='history_delete_upload'),
    path('user_downloads/', views.user_downloads, name='history_user_uploads'),
]