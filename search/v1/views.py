from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.response import Response
from rest_framework import status
from django.utils.text import slugify
from django.db.models import Q
from django.db.models import QuerySet
from rest_framework.pagination import CursorPagination

from authentication.customauth import CustomAuthBackend, IsConsumer
from mediacontent.models import PodcastEpisode
from .serializers import SearchContentSerializer
from playback.constants import MediaTypes


class CustomCursorPagination(CursorPagination):
    page_size = 5
    ordering = '-published_at'
    cursor_query_param = 'cursor'


@api_view(['GET'])
@permission_classes([IsConsumer])
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
@permission_classes([IsConsumer])
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
@permission_classes([IsConsumer])
@authentication_classes([CustomAuthBackend])
def save_search_history(request):

    update_or_create(
        content_type=content_type_model,
        object_id=episode_id,
        user=request.user,
        defaults={
            'content_progress': content_progress
        }
    )
    pass