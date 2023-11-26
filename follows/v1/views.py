from django.db import IntegrityError
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.response import Response
from rest_framework import status

from authentication.customauth import IsAuthenticated, CustomAuthBackend
import follows.v1.service as RelationService
import asyncio


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([CustomAuthBackend])
def follow_user(request):
    user_id = request.user.id
    followee_id = request.data.get('followee_id')

    try:
        success = asyncio.run(RelationService.follow_user(user_id=user_id, followee_id=followee_id))
        return Response(data={'success': success}, status=status.HTTP_200_OK)
    except IntegrityError:
        return Response(data={'message': 'Invalid followee id'}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
    except Exception as e:
        return Response(data={'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([CustomAuthBackend])
def unfollow_user(request):
    user_id = request.user.id
    followee_id = request.data.get('followee_id')

    try:
        success = asyncio.run(RelationService.unfollow_user(user_id=user_id, followee_id=followee_id))
        return Response(data={'success': success}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response(data={'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([CustomAuthBackend])
def get_follow_info(request, related_user_id):
    user_id = request.user.id

    try:
        follow_data = asyncio.run(RelationService.get_follow_relation(user_id=user_id, related_user_id=related_user_id))
        return Response(data={'data': follow_data}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response(data={'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([CustomAuthBackend])
def followings_list(request):
    user_id = request.user.id

    try:
        follwing_list = asyncio.run(RelationService.find_followed_users_contents(request=request, user_id=user_id))
        return Response(data={'data': follwing_list}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response(data={'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)


