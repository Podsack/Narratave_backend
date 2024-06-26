from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.response import Response

from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from authentication.customauth import CustomAuthBackend
from rest_framework.permissions import IsAuthenticated
from .serializers import CategorySerializer, SectionSerializer, PodcastSeriesSerializer, PodcastEpisodeSerializer
from ..models import Category, Section, PodcastSeries, PodcastEpisode


episode_select_fields = ['id', 'slug', 'title', 'duration_in_sec', 'audio_metadata', 'covers', 'episode_no']

@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([CustomAuthBackend])
def retrieve_content_categories(request):
    content_categories = Category.objects.all()
    serializer = CategorySerializer(content_categories, many=True)
    return Response(data={'content_categories': serializer.data}, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([CustomAuthBackend])
def get_dashboard_sections(request):
    sections = Section.objects.filter(active=True).order_by('priority')
    serializer = SectionSerializer(sections, many=True)
    return Response(data={'sections': serializer.data}, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([CustomAuthBackend])
def get_customer_history(request):
    sections = Section.objects.filter(active=True)
    serializer = SectionSerializer(sections)
    return Response(data={'content_categories': serializer.data}, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([CustomAuthBackend])
def get_podcast_series_by_id(request, podcast_series_id):
    podcast_series = PodcastSeries.objects.filter(id=podcast_series_id)\
        .only(*['id', 'name', 'description', 'published_episode_count', 'published', 'covers'])\
        .first()

    if podcast_series is None:
        return Response(data={'message': 'Podcast series id not found'}, status=status.HTTP_404_NOT_FOUND)

    return Response(data=PodcastSeriesSerializer(podcast_series).data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([CustomAuthBackend])
def get_podcast_episode_by_slug(request, podcast_episode_slug):
    podcast_episode = PodcastEpisode.objects.filter(id=podcast_episode_slug).first()

    if podcast_episode is None:
        return Response(data={'message': 'Podcast series id not found'}, status=status.HTTP_404_NOT_FOUND)

    return Response(data=PodcastEpisodeSerializer(podcast_episode).data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([CustomAuthBackend])
def get_episodes_by_podcast(request, podcast_series_id):
    from_episode = request.GET.get('from')
    page_size = request.GET.get('page_size')
    order = request.GET.get('order') or 'DESC'

    if (from_episode is None or not from_episode.isdigit()) or (page_size is None or not page_size.isdigit()):
        return Response(data={"message": "Invalid episode range"}, status=status.HTTP_400_BAD_REQUEST)

    if order is not None and order not in {'ASC', 'DESC'}:
        return Response(data={"message": "Order should be one of ASC or DESC"}, status=status.HTTP_400_BAD_REQUEST)

    to_episode = int(from_episode) + (-1 if order is 'DESC' else 1) * int(page_size)

    lower_limit, upper_limit = (to_episode, int(from_episode)) if order is 'DESC' else (int(from_episode), to_episode)

    podcast_episodes = PodcastEpisode.objects\
        .filter(podcast_series=podcast_series_id, episode_no__lte=upper_limit, episode_no__gt=lower_limit, published=True,) \
        .prefetch_related('featured_artists') \
        .only(*episode_select_fields) \
        .order_by('-episode_no' if order is 'DESC' else 'episode_no')

    try:
        serialized_podcast_episodes = PodcastEpisodeSerializer(podcast_episodes, many=True)
        return Response(data={'episodes': serialized_podcast_episodes.data}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response(data={"message": str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([CustomAuthBackend])
def get_podcast_episodes_by_ids(request):
    """
    This API is exposed for doing id__in queries
    """
    try:
        podcast_episode_query = request.query_params.get('episode_ids')

        if podcast_episode_query is None or podcast_episode_query == '':
            return Response(data={'message': 'Invalid podcast episode ids'}, status=status.HTTP_400_BAD_REQUEST)

        podcast_episode_ids = list(map(int, podcast_episode_query.split(',')))

        if podcast_episode_ids is not None and isinstance(podcast_episode_ids, list) and len(podcast_episode_ids) == 0:
            return Response(data={'message': 'Invalid podcast episode ids'}, status=status.HTTP_400_BAD_REQUEST)

        podcast_episodes = PodcastEpisode.objects.filter(id__in=podcast_episode_ids).prefetch_related('featured_artists')\
            .only(*episode_select_fields)

        serialized_podcast_episodes = PodcastEpisodeSerializer(podcast_episodes, many=True)
        return Response(data={'episodes': serialized_podcast_episodes.data}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response(data={"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
