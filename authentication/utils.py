from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.backends import TokenBackend
from rest_framework.exceptions import ValidationError
from .models import UserSession
from datetime import datetime, timedelta
from django.conf import settings


class AuthUtils:
    @staticmethod
    def generate_token(request, user):
        refresh_token = RefreshToken.for_user(user)
        token = {
            'refresh_token': str(refresh_token),
            'access_token': str(refresh_token.access_token),
        }
        user_session = UserSession(id=None, session_key=str(refresh_token),
                                   ip_address=AuthUtils.get_client_ip_address(request),
                                   user=user,
                                   expired_at=datetime.now() + settings.SIMPLE_JWT.get('REFRESH_TOKEN_LIFETIME'))
        user_session.save()
        return token

    @staticmethod
    def get_user_from_token(request):
        authorization_header = request.META.get('Authorization')

        if authorization_header is not None:
            try:
                token = authorization_header.split(' ')[1]
                valid_data = TokenBackend(algorithm='HS256').decode(token, verify=True)
                user = valid_data['user']
                return user
            except ValidationError as v:
                print("validation error", v)
            except Exception as e:
                print("validation error", e)
        return None

    @staticmethod
    def get_client_ip_address(request):
        req_headers = request.META
        x_forwarded_for_value = req_headers.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for_value:
            ip_addr = x_forwarded_for_value.split(',')[-1].strip()
        else:
            ip_addr = req_headers.get('REMOTE_ADDR')
        return ip_addr