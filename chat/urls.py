from django.urls import path
from . import views


urlpatterns = [
    path('open_ai/', views.PromptSubmissionViewSet.as_view(), name='open_ai'),
    path('open_ai/summarize/', views.summarize, name='open_ai_summarize'),
]
