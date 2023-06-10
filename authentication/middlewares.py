from django.core.exceptions import PermissionDenied
from .models import UserSession


class SessionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.session.get('session_key') is not None:
            session_key = request.session.get('session_key')
        elif request.headers.get('auth_token') is not None:
            session_key = request.headers.get('auth_token')
        else:
            raise PermissionDenied("Your session is invalid")

        response = self.get_response(request)
        return response
        # if UserSession.objects.get(session_key=session_key):
