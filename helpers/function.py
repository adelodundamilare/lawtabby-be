
from django.http import JsonResponse
from rest_framework import status
from django.contrib.sites.shortcuts import get_current_site
from django.conf import settings
from decouple import config

from history.repository import HistoryRepository


def SuccessResponse(message: str = 'Action Successful', data: dict = None, status_code: int = status.HTTP_200_OK, safe: bool = True) -> JsonResponse:
    response_data = {
        "success": True,
        "message": message
    }

    if data is not None:
        response_data["data"] = data

    return JsonResponse(response_data, status=status_code, safe=safe)

def FailedResponse(error: str = None, status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR, safe: bool = True) -> JsonResponse:
    message: str = 'Unable to complete action, please try again or contact support',

    return JsonResponse({
        "success": False,
        "message": error if error else message
    }, status=status_code, safe=safe)

def add_to_history(user, title):
    history_repo = HistoryRepository()
    history_repo.create({
        'user':user,
        'title':title
    })

def compute_file_url(file_name):
    base_url = config('BACKEND_URL')
    return f"{base_url}{settings.MEDIA_URL}{file_name}"