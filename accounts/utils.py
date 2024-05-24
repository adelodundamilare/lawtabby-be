import json
from typing import Any, Dict
from django.core.mail import send_mail
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from pydantic import ValidationError
from .models import User
from rest_framework.authtoken.models import Token
import requests
from decouple import config
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

GOOGLE_ID_TOKEN_INFO_URL = 'https://www.googleapis.com/oauth2/v3/tokeninfo'
GOOGLE_ACCESS_TOKEN_OBTAIN_URL = 'https://oauth2.googleapis.com/token'
GOOGLE_USER_INFO_URL = 'https://www.googleapis.com/oauth2/v3/userinfo'

def send_email_verification_code(email, verification_code):
    subject = 'Verify Your Email Address'
    message = f'Your email verification code is: {verification_code}'
    from_email = 'noreply@example.com'
    recipient_list = [email]
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipient_list)



def generate_tokens_for_user(user):
    """
    Generate access and refresh tokens for the given user
    """
    serializer = TokenObtainPairSerializer()
    token_data = serializer.get_token(user)
    access_token = token_data.access_token
    refresh_token = token_data
    return access_token, refresh_token


def google_get_access_token(code: str) -> str:

    client_id = config('GOOGLE_CLIENT_ID')
    client_secret = config('GOOGLE_CLIENT_SECRET')

    payload = {
        'code': code,
        'client_id': client_id,
        'client_secret': client_secret,
        'redirect_uri': 'postmessage',
        'grant_type': 'authorization_code'
    }

    response = requests.post(GOOGLE_ACCESS_TOKEN_OBTAIN_URL, data=payload)

    if not response.ok:
        raise ValidationError('Failed to obtain access token from Google.')

    access_token = response.json()['access_token']

    return access_token


def google_get_user_info( access_token:  str) -> Dict[str, Any]:
    GOOGLE_USER_INFO_URL = 'https://www.googleapis.com/oauth2/v3/userinfo'

    response = requests.get(
        GOOGLE_USER_INFO_URL,
        params={'access_token': access_token}
    )

    if not response.ok:
        raise ValidationError('Failed to obtain user info from Google.')

    return response.json()


def get_token(user_info):
    email = user_info.get('email')
    name = user_info.get('name')
    avatar = user_info.get('picture')

    user = None

    try:
        user = User.objects.get(email=email)
    except Exception as e:
        print(e)

    if not user:
        user = User.objects.create(
            email=email,
            name=name,
            avatar=avatar
        )

    token = Token.objects.get(user=user)
    token_to_str = str(token)
    token_to_json = json.dumps(token_to_str)
    token_to_load = json.loads(token_to_json)

    return token_to_load