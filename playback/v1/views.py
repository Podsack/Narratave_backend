from typing import Dict, Any

from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.response import Response
from rest_framework import status
from django.contrib.contenttypes.models import ContentType
from rest_framework.serializers import ValidationError
import asyncio

from authentication.customauth import CustomAuthBackend
from rest_framework.permissions import IsAuthenticated
from mediacontent.models import PodcastEpisode
from playback.utils import get_generic_content_value, transform_history_dict
from ..constants import MediaTypes
from ..models import ContentHistory
from .serializers import PlaybackHistoryRequestSerializer


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([CustomAuthBackend])
def save_playback_history(request):
    episode_id = request.data.get('episode_id')
    start = request.data.get('start')
    end = request.data.get('end')
    object_type = request.data.get('object_type')
    content_type = None

    request_serializer = PlaybackHistoryRequestSerializer(data=request.data)

    try:
        if request_serializer.is_valid(raise_exception=True):
            if object_type == MediaTypes.PODCAST.name:
                content_type = ContentType.objects.get_for_model(MediaTypes.PODCAST.value)

            if content_type is not None:
                asyncio.run(request_serializer.async_save(user=request.user, content_type=content_type))

                if object_type == MediaTypes.PODCAST.name:
                    asyncio.run(PodcastEpisode.increase_play_count(instance_id=episode_id))

                return Response(data={'success': True}, status=status.HTTP_200_OK)
            else:
                return Response(data={'message': 'Received invalid content type'}, status=status.HTTP_400_BAD_REQUEST)
    except ValidationError as e:
        return Response(data={'message': request_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response(data={'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([CustomAuthBackend])
def get_history_by_user(request):
    page_size = request.GET.get('page_size')
    last_played = request.GET.get('last_played')
    include_artist = request.GET.get('include_artist')
    include_series = request.GET.get('include_series')

    try:
        content_histories = ContentHistory.get_histories_by_user(user_id=request.user.id, months_ago=3,
                                                                 last_played_time=last_played, page_size=page_size)

        model_ids_mapping: Dict[int, Dict[int, Any]] = {}

        prev_last_played_at = None

        for history in content_histories:
            content_type = history.content_type_id
            prev_last_played_at = history.last_played_at if prev_last_played_at is None else min(history.last_played_at, prev_last_played_at)

            if content_type not in model_ids_mapping:
                model_ids_mapping[content_type] = {}
            if history.object_id not in model_ids_mapping[content_type]:
                model_ids_mapping[content_type][history.object_id] = None

        for model_type in model_ids_mapping:
            model_content_type = ContentType.objects.get_for_id(model_type)
            model_class = model_content_type.model_class()
            model_id_list = list(model_ids_mapping[model_type].keys())
            contents = get_generic_content_value(model_class=model_class, id_list=model_id_list, include_artist=include_artist, include_series=include_series)

            for content in contents:
                model_ids_mapping[model_type][content['id']] = content

        hist_result = transform_history_dict(content_histories=content_histories, model_ids_mapping=model_ids_mapping, prev_last_played=prev_last_played_at)

        return Response(data=hist_result, status=status.HTTP_200_OK)
    except Exception as e:
        return Response(data={'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)


async def run_coroutine(*args):
    return asyncio.gather(*args)
