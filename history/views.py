
import traceback
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from helpers.function import FailedResponse, SuccessResponse
from history.serializers import HistorySerializer
from . import utils

# Create your views here.

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def all(request):
    try:
        user = request.user
        history = utils.find_all(user)
        data = HistorySerializer(history, many=True).data
        return SuccessResponse(message='History fetched successfully', data=data, status_code=200)

    except Exception as e:
        traceback.print_exc()
        return FailedResponse(error= f'{str(e)}', status_code=500)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def latest(request):
    try:
        user = request.user
        history = utils.latest(user)
        data = HistorySerializer(history, many=True).data
        return SuccessResponse(message='History fetched successfully', data=data, status_code=200)

    except Exception as e:
        traceback.print_exc()
        return FailedResponse(error= f'{str(e)}', status_code=500)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_uploads(request):
    try:
        user = request.user
        history = utils.fetch_user_uploads(user)
        return SuccessResponse(message='User Uploads fetched successfully', data=history, status_code=200)

    except Exception as e:
        traceback.print_exc()
        return FailedResponse(error= f'{str(e)}', status_code=500)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def rename_upload(request):
    try:
        user = request.user
        name = request.data.get('name')
        id = request.data.get('id')

        if not name or not id:
            return FailedResponse(error='Name or ID is required', status_code=500)

        utils.rename_upload(user, id, name)
        return SuccessResponse(message='File renamed successfully', status_code=200)

    except Exception as e:
        traceback.print_exc()
        return FailedResponse(error= f'{str(e)}', status_code=500)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_upload(request, id):
    try:
        user = request.user

        utils.delete_upload(user, id=id)
        return SuccessResponse(message='File deleted successfully', status_code=200)

    except Exception as e:
        traceback.print_exc()
        return FailedResponse(error= f'{str(e)}', status_code=500)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_downloads(request):
    try:
        user = request.user
        history = utils.fetch_user_downloads(user)
        return SuccessResponse(message='User Downloads fetched successfully', data=history, status_code=200)

    except Exception as e:
        traceback.print_exc()
        return FailedResponse(error= f'{str(e)}', status_code=500)