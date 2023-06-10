from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth import get_user_model
from .utils import AuthUtils

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
        role = "CONSUMER" if request.data.get('role') is None else request.data.get('role')
        password = request.data.get('password')

        user = User.objects.filter(email=email, role=role).first()

        if password is not None and user is not None and user.check_password(password):
            return user
