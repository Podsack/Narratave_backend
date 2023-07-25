from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework.exceptions import ValidationError, APIException
from datetime import timedelta
from django.utils import timezone
from django.conf import settings
from django.contrib.auth import get_user_model
from asgiref.sync import sync_to_async
from firebase_admin import auth

from ..models import UserSession


User = get_user_model()


class AuthUtils:
    @staticmethod
    async def generate_token(request, user, check_for_session=True):
        refresh_token = RefreshToken.for_user(user)
        token = {
            'refresh_token': str(refresh_token),
            'access_token': str(refresh_token.access_token),
        }

        current_ip = AuthUtils.get_client_ip_address(request)
        user_session = None
        new_exp = timezone.now() + settings.SIMPLE_JWT.get('REFRESH_TOKEN_LIFETIME')

        if check_for_session:
            user_session = await sync_to_async(UserSession.objects.filter(user=user, ip_address=current_ip).first)()

        if user_session is not None:
            user_session.ip_address = current_ip
            user_session.session_key = str(refresh_token)
            user_session.expired_at = new_exp
        else:
            user_session = UserSession(id=None, session_key=str(refresh_token),
                                       ip_address=current_ip,
                                       user=user,
                                       expired_at=new_exp)
        await sync_to_async(user_session.save)()
        return token

    @staticmethod
    def get_user_from_token(request):
        authorization_header = request.META.get('HTTP_AUTHORIZATION')

        if authorization_header is not None:
            try:
                user = None
                token = authorization_header.split(' ')[1]
                valid_data = AccessToken(token)
                user_id = valid_data.get('user_id')

                # TODO Cache the frequently accessed user
                if user_id is not None:
                    user = User.objects.filter(id=user_id).first()
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

    @staticmethod
    def get_new_access_token(refresh_token):
        try:
            old_refresh_token = RefreshToken(token=refresh_token)
            user_session = UserSession.objects.select_related('user').filter(session_key=str(old_refresh_token)).first()

            if user_session is None:
                raise APIException("User session doesn't exist")

            user = user_session.user
            new_refresh_token = RefreshToken.for_user(user=user)

            user_session.session_key = str(new_refresh_token)
            user_session.expired_at = timezone.now() + timedelta(days=7)
            user_session.save()

            return str(new_refresh_token), str(new_refresh_token.access_token)
        except TokenError as e:
            raise APIException("Token Expired") from e


    @staticmethod
    def delete_session(user):
        user_session = UserSession.objects.filter(user=user).first()

        if user_session is None:
            raise APIException("User session doesn't exist")

        user_session.delete()
        return True

    @staticmethod
    def validate_google_id_token(id_token):
        decoded_token = auth.verify_id_token(id_token)
