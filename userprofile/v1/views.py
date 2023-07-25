from rest_framework.response import Response
from rest_framework.decorators import authentication_classes, permission_classes, api_view
from asgiref.sync import async_to_sync
import rest_framework.status as status
import asyncio

from ..models import Preference
from authentication.customauth import CustomAuthBackend, IsConsumer
from ..utils.app_language_loader import AppLanguageLoader
from .serializers import UserPreferenceSerializer


@api_view(['GET'])
@permission_classes([IsConsumer])
@authentication_classes([CustomAuthBackend])
# @sync_to_async
def retrieve_app_languages(request):
    country = request.GET.get('country')
    state = request.GET.get('state')

    if country is None or state is None:
        user_preference = async_to_sync(UserPreferenceSerializer().get_by_user_id)(user_id=request.user.pk)
        country = user_preference.country
        state = user_preference.state

    app_languages = AppLanguageLoader().get_app_language(country=country, state=state)

    return Response(data={'app_languages': app_languages}, status=status.HTTP_200_OK)


@api_view(['PUT'])
@permission_classes([IsConsumer])
@authentication_classes([CustomAuthBackend])
def update_preferences(request):
    try:
        update_resp = Preference.objects.filter(user_id=request.user.pk).update(**request.data)

        if update_resp == 1:
            return Response(data={'message': 'User preference saved'}, status=status.HTTP_200_OK)
        else:
            return Response(data={'message': 'User preference cannot be saved'}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response(data={'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)
