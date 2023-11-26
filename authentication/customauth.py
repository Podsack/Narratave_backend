from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from authentication.models import UserSession
from .utils.auth_utils import AuthUtils

User = get_user_model()


class CustomAuthBackend(BaseAuthentication):
    def authenticate(self, request):
        user = AuthUtils.get_user_from_token(request)

        if user is None:
            raise AuthenticationFailed('User not found')

        request.user = user
        return user, None


    @staticmethod
    def authenticate_with_password(request):
        email = request.data.get('email')
        password = request.data.get('password')

        user = User.objects.filter(email=email).first()

        if password is not None and user is not None and user.check_password(password):
            return user


class IsConsumer(IsAuthenticated):
    def has_permission(self, request, view) -> bool:
        return bool(super().has_permission(request, view) and request.user.role == 'CONSUMER')


class IsAuthor(IsAuthenticated):
    def has_permission(self, request, view) -> bool:
        return bool(super().has_permission(request, view) and request.user.role == 'AUTHOR')


class IsArtist(IsAuthenticated):
    def has_permission(self, request, view) -> bool:
        return bool(super().has_permission(request, view) and request.user.role == 'ARTIST')
