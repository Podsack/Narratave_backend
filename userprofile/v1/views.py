from rest_framework.response import Response
from rest_framework.decorators import authentication_classes, permission_classes, api_view
from rest_framework.permissions import IsAuthenticated
from authentication.customauth import CustomAuthBackend
import httpx
from asgiref.sync import sync_to_async
import rest_framework.status as status
from .serializers import UserPreferenceSerializer


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([CustomAuthBackend])
# TODO add @sync_to_async annotation
async def retrieve_app_languages(request):
    # if request.method is not 'GET':
    #     return Response(data={}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    data = None
    async with httpx.AsyncClient() as client:
        # {AuthUtils.get_client_ip_address(request)}
        url = f'https://ipinfo.io/103.203.63.150/json'
        response = await client.get(url)

        if response.status_code == httpx.codes.OK:
            data = response.json()

    serializer = UserPreferenceSerializer(data={'state': data.get('region'), 'country':data.get('country'), 'user': request.user.pk})

    try:
        if serializer.is_valid():
            serializer.save()
    except Exception as e:
        return Response(data={}, status=status.HTTP_400_BAD_REQUEST)

    return Response(data={}, status=status.HTTP_400_BAD_REQUEST)
