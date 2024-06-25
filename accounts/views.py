import traceback
from django.http import JsonResponse
from django.shortcuts import render
from accounts.models import User, Token
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import update_session_auth_hash
from accounts.serializers import MyTokenObtainPairSerializer, UserSerializer, ChangePasswordSerializer, UserProfileSerializer
from rest_framework import generics
from django.conf import settings
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from rest_framework.decorators import api_view, permission_classes
from accounts.utils import get_token, google_get_access_token, google_get_user_info
from helpers.function import add_to_history
from history.repository import HistoryRepository
from project.settings import  GOOGLE_REDIRECT_URL, MICROSOFT_REDIRECT_URL, APPlE_REDIRECT_URL
from rest_framework import serializers, status
from decouple import config
#google login
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from google.oauth2 import id_token
from google.auth.transport import requests
from dj_rest_auth.registration.views import SocialLoginView
#Microsoft login
from allauth.socialaccount.providers.microsoft.views import MicrosoftGraphOAuth2Adapter
#apple login
from allauth.socialaccount.views import SignupView
from allauth.socialaccount.providers.apple.views import AppleOAuth2Adapter
# from allauth.socialaccount.providers.apple.client import AppleOAuth2Client
from .apple_utils import AppleOAuth2Client
from allauth.socialaccount.providers.oauth2.views import OAuth2Error
from urllib.parse import unquote
#Mredirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import RedirectView



class UserRegistrationView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({'message': 'User Successfully Created'})
        except serializers.ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)



class EmailVerificationAPIView(APIView):
    def get(self, request, verification_code):
        try:
            user = User.objects.get(email_verification_code=verification_code, is_active=False)
        except User.DoesNotExist:
            return Response({'message': 'Invalid verification code'}, status=status.HTTP_400_BAD_REQUEST)
        user.is_active = True
        user.save()
        token, _ = Token.objects.get_or_create(user=user)
        return Response({'message': 'Email verified successfully',
                         'token': token.key
                         },
                        status=status.HTTP_200_OK)



class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)

        if serializer.is_valid():
            user = request.user
            if user.check_password(serializer.data.get('old_password')):
                user.set_password(serializer.data.get('new_password'))
                user.save()
                update_session_auth_hash(request, user)
                return Response({'message': 'Password changed successfully.'}, status=status.HTTP_200_OK)
            return Response({'error': 'Incorrect old password.'}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile(request):
    user = request.user
    query = User.objects.filter(email=user.email).first()
    serializer = UserProfileSerializer(query)

    # remove unwanted /media from avatar response
    data = serializer.data
    avatar = data.get('avatar')
    if avatar and isinstance(avatar, str) and data['avatar'].startswith('/media/'):
        data['avatar'] = unquote(data['avatar'])[len('/media/'):]

    return JsonResponse({'data': data})


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def put_update_name(request):
    name = request.data.get('name')

    if not name:
        return JsonResponse('Name is required', status=400)

    user = request.user
    user.name = name
    user.save()

    return JsonResponse({'message': "Name has successfully been updated."})

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def put_update_avatar(request):
    avatar = request.data.get('avatar')

    if not avatar:
        return JsonResponse('Avatar is required', status=400)

    user = request.user
    user.avatar = avatar
    user.save()

    add_to_history(user=user, title='Profile photo updated')

    return JsonResponse({'message': "Avatar has successfully been updated."})


@api_view(['POST'])
def post_google_login(request):
    try:
        token = request.data.get('code')
        access_token = google_get_access_token(code=token)

        user_info = google_get_user_info(access_token)

        token = get_token(user_info)

        return JsonResponse({'message': 'Login successful', 'token': token, 'email': user_info.get('email')})

    except Exception as e:
        traceback.print_exc()
        return JsonResponse({'message': 'Unable to login with Google Auth, please try again', 'error': f'{str(e)}'}, status=500)





class UserRedirectView(LoginRequiredMixin, RedirectView):
    """
    This view is needed by the dj-rest-auth-library in order to work the google login. It's a bug.
    """

    permanent = False

    def get_redirect_url(self):
        return "redirect-url"



class MicrosoftLoginView(SocialLoginView):
    adapter_class = MicrosoftGraphOAuth2Adapter
    callback_url = MICROSOFT_REDIRECT_URL
    client_class = OAuth2Client

    @property
    def username(self):
        return self.adapter.user.email



class AppleLoginView(SocialLoginView):
    adapter_class = AppleOAuth2Adapter
    callback_url = APPlE_REDIRECT_URL
    client_class = AppleOAuth2Client


    def post(self, request, *args, **kwargs):
        try:
            return super().post(request, *args, **kwargs)
        except OAuth2Error as e:
            # Handle the OAuth2Error here
            error_message = str(e)
            return Response({"error": error_message}, status=status.HTTP_400_BAD_REQUEST)

    @property
    def username(self):
        return self.adapter.user.email





