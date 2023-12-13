import asyncio
from typing import Dict, Any
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.response import Response
from rest_framework import status
from django.utils.text import slugify
from django.db.models import Q
from django.db.models import QuerySet
from rest_framework.pagination import CursorPagination

from authentication.customauth import CustomAuthBackend
from mediacontent.models import PodcastEpisode, PodcastSeries
from rest_framework.permissions import IsAuthenticated
from activity.models import Log, ActivityTypeEnum
from playback.utils import get_generic_content_value
from .serializers import SearchContentSerializer
from activity.utils import transform_activity_dict


class CustomCursorPagination(CursorPagination):
    page_size = 5
    ordering = '-published_at'
    cursor_query_param = 'cursor'


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([CustomAuthBackend])
def search_content(request):
    keyword = request.GET.get('search')
    category = request.GET.get('category')
    title_slug = slugify(keyword)

    def get_queryset():
        qs: QuerySet = None

        if keyword is not None:
            qs = PodcastEpisode.objects.filter(
                Q(published=True) &
                (
                        Q(slug__icontains=title_slug) |
                        Q(categories__icontains=keyword) |
                        Q(tags__icontains=keyword)
                )

            )
        elif category is not None:
            qs = PodcastEpisode.objects.filter(
                Q(published=True) & Q(categories__contains=category)
            )

        return qs.select_related('podcast_series') \
            .only('id', 'title', 'published_at', 'podcast_series__name', 'podcast_series__published_episode_count',
                  'play_count', 'episode_no', 'covers')

    paginator = CustomCursorPagination()
    paginated_data = paginator.paginate_queryset(queryset=get_queryset(), request=request)

    serialized_data = SearchContentSerializer(paginated_data, many=True)
    return Response(data={'data': serialized_data.data, 'next': paginator.get_next_link()}, status=status.HTTP_200_OK)


# TODO: Tries or balanced BST for searching
@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([CustomAuthBackend])
def get_search_tags(request):
    keyword = request.GET.get('search')
    if keyword is None:
        return Response(data={'message': 'Invalid search keyword'}, status=status.HTTP_400_BAD_REQUEST)
    '''
    1. Tags can be searched with it's name ordered by latest and also trending
    '''
    title_slug = slugify(keyword)
    podcast_series_list = PodcastEpisode.objects.filter(
        Q(published=True) & (Q(title__istartswith=keyword) | Q(slug__startswith=title_slug))) \
                              .order_by('-play_count').values_list('title', flat=True)[:10]

    return Response(data=podcast_series_list, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([CustomAuthBackend])
def save_search_history(request):
    content_id = request.data.get('content_id')
    content_type = request.data.get('content_type')

    try:
        asyncio.run(Log.objects.acreate(
            activity_type=ActivityTypeEnum.search.value,
            user=request.user,
            content_type=content_type,
            content_id=content_id,
        ))
        return Response(data={'success': True}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response(data={'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([CustomAuthBackend])
def get_recent_searches(request):
    last_timestamp = request.GET.get('last_timestamp')
    if request.user is None:
        return Response(data={'message': 'User is not provided'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        activities = Log.get_activities_by_user(
            user_id=request.user.id,
            months_ago=3,
            last_played_time=last_timestamp,
            activity_type=ActivityTypeEnum.search.value
        )

        model_ids_mapping: Dict[int, Dict[int, Any]] = {}

        prev_last_timestamp = None

        for activity in activities:
            content_type = activity.content_type
            prev_last_timestamp = activity.timestamp if prev_last_timestamp is None else min(activity.timestamp, prev_last_timestamp)

            if content_type not in model_ids_mapping:
                model_ids_mapping[content_type] = {}

            if activity.content_id not in model_ids_mapping[content_type]:
                model_ids_mapping[content_type][activity.content_id] = None

        for model_type in model_ids_mapping:
            model_class = get_model_class(model_type)
            model_id_list = list(model_ids_mapping[model_type].keys())
            contents = get_generic_content_value(model_class=model_class, id_list=model_id_list)

            for content in contents:
                model_ids_mapping[model_type][content['id']] = content

        hist_result = transform_activity_dict(activity_history=activities, model_ids_mapping=model_ids_mapping, prev_last_played=prev_last_timestamp)

        return Response(data=hist_result, status=status.HTTP_200_OK)
    except Exception as e:
        return Response(data={'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)


def get_model_class(model_type_name):
    if PodcastEpisode._meta.model_name == model_type_name:
        return PodcastEpisode
    elif PodcastSeries._meta.model_name == model_type_name:
        return PodcastSeries
    else:
        return None
