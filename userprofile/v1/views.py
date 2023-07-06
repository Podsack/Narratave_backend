from rest_framework.response import Response
from rest_framework.decorators import authentication_classes, permission_classes, api_view
from rest_framework.permissions import IsAuthenticated
from asgiref.sync import sync_to_async
import rest_framework.status as status
import asyncio

from authentication.customauth import CustomAuthBackend
from ..utils.httpclients import IPClient
from ..utils.app_language_loader import AppLanguageLoader
from .serializers import UserPreferenceSerializer
from authentication.utils import AuthUtils


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([CustomAuthBackend])
# @sync_to_async
def retrieve_app_languages(request):
    current_ip = AuthUtils.get_client_ip_address(request)
    ip_client = IPClient()
    event_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(event_loop)
    location_data = event_loop.run_until_complete(ip_client.get_ip_address(ip=current_ip))
    app_languages = AppLanguageLoader().get_app_language(country=location_data.get('country') or "IN", state=location_data.get('region') or "West Bengal")

    serializer = UserPreferenceSerializer(
        data={
            'state': location_data.get('region'),
            'country': location_data.get('country'),
            'user': request.user.pk,
        }
    )

    try:
        if serializer.is_valid():
            serializer.save()
    except Exception as e:
        return Response(data={}, status=status.HTTP_400_BAD_REQUEST)

    return Response(data={'app_languages': app_languages}, status=status.HTTP_400_BAD_REQUEST)
