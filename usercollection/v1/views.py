from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError
from django.db import transaction
from django.db.utils import IntegrityError

from functools import reduce

from authentication.customauth import CustomAuthBackend
from ..models import Playlist
from rest_framework.permissions import IsAuthenticated
from Narratave.exceptions import ForbiddenError
from mediacontent.models import PodcastSeries
from .serializers import PlaylistWriteSerializer, PlaylistReadonlySerializer, PodcastEpisodeSerializer
from ..utils import add_duration, get_cover_from_list


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([CustomAuthBackend])
def create_playlist(request):
    user_id = request.user.id
    podcast_ids = request.data.get('podcast_ids')

    if podcast_ids is None or len(podcast_ids) == 0:
        return Response(data={'message': 'Playlist must have atleast one item'},
                        status=status.HTTP_400_BAD_REQUEST)

    podcast_series_episodes_list = PodcastSeries.objects.filter(id__in=podcast_ids).prefetch_related('podcastepisode_set').values('podcastepisode__covers')

    playlist_serializer = PlaylistWriteSerializer(
        data={
            **request.data,
            'owner': user_id,
            'covers': get_cover_from_list(podcast_series_episodes_list),
        })

    try:
        if playlist_serializer.is_valid(raise_exception=True):
            playlist_serializer.save()
            return Response(data={'message': 'Playlist created', 'data': playlist_serializer.data},
                            status=status.HTTP_201_CREATED)
    except ValidationError:
        return Response(data={'message': playlist_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    except IntegrityError as ie:
        if str(ie).index('unique_playlist_per_owner') > -1:
            return Response(data={'message': 'A playlist already exists with this name'},
                            status=status.HTTP_400_BAD_REQUEST)
        return Response(data={'message': str(ie)},
                        status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([CustomAuthBackend])
def create_favorite_playlist(request):
    user_id = request.user.id
    podcast_ids = request.data.get('podcast_ids')
    podcast_details_list = PodcastSeries.objects.filter(id__in=podcast_ids).prefetch_related('podcastepisode_set').values('podcastepisode__duration_in_sec', 'podcastepisode__covers')
    total_time = reduce(add_duration, podcast_details_list, 0)

    playlist_serializer = PlaylistWriteSerializer(
        data={
            **request.data,
            'title': Playlist.FAVORITE_PLAYLIST_NAME,
            'owner': user_id,
            'covers': get_cover_from_list(podcast_details_list),
            'is_required': True
        })

    try:
        if playlist_serializer.is_valid(raise_exception=True):
            playlist_serializer.save()
            return Response(data={'message': 'Playlist created', 'data': playlist_serializer.data},
                            status=status.HTTP_201_CREATED)
    except ValidationError:
        return Response(data={'message': playlist_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    except IntegrityError as ie:
        if str(ie).index('unique_playlist_per_owner') > -1:
            return Response(data={'message': 'A playlist already exists with this name'},
                            status=status.HTTP_400_BAD_REQUEST)
        return Response(data={'message': str(ie)},
                        status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
@authentication_classes([CustomAuthBackend])
def update_playlist(request):
    new_podcast_ids_map = request.data.get('new_podcast_ids_map')

    try:
        Playlist.update_podcast_ids(playlist_podcast_ids_mapping=new_podcast_ids_map)
        return Response(data={'success': True}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response(data={'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
@authentication_classes([CustomAuthBackend])
@transaction.atomic
def add_podcast_to_playlist(request, playlist_id):
    user_id = request.user.id
    podcast_id = request.data.get('podcast_id')

    try:
        current_playlist: Playlist = Playlist.objects.filter(id=playlist_id).only('id', 'title', 'owner_id',
                                                                                  'is_private',
                                                                                  'is_required',
                                                                                  'podcast_ids',
                                                                                  'covers').first()

        if current_playlist is None:
            return Response(data={'message': 'Playlist not found'}, status=status.HTTP_404_NOT_FOUND)

        if current_playlist.owner_id != user_id:
            return Response(data={'message': 'User is not the owner'}, status=status.HTTP_403_FORBIDDEN)

        current_playlist.add_podcast_id_to_playlist(podcast_id)

        return Response(data={'data': PlaylistReadonlySerializer(current_playlist).data},
                        status=status.HTTP_200_OK)
    except ForbiddenError as fe:
        return Response(data={'message': str(fe)}, status=status.HTTP_403_FORBIDDEN)
    except Exception as e:
        return Response(data={'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
@authentication_classes([CustomAuthBackend])
@transaction.atomic
def add_podcast_to_favorites(request):
    user_id = request.user.id
    podcast_id = request.data.get('podcast_id')

    try:
        current_playlist: Playlist = Playlist.objects.filter(title=Playlist.FAVORITE_PLAYLIST_NAME, owner=user_id).only(
            'id', 'title', 'owner_id',
            'is_required',
            'is_private',
            'podcast_ids',
            'covers',
            'total_podcast_count').first()

        if current_playlist is None:
            current_playlist = create_playlist_by_title(playlist_title=Playlist.FAVORITE_PLAYLIST_NAME, user_id=user_id)

        if current_playlist.owner_id != user_id:
            return Response(data={'message': 'User is not the owner'}, status=status.HTTP_403_FORBIDDEN)

        current_playlist.add_podcast_id_to_playlist(podcast_id)

        return Response(data={'data': PlaylistReadonlySerializer(current_playlist).data},
                        status=status.HTTP_200_OK)
    except ForbiddenError as fe:
        return Response(data={'message': str(fe)}, status=status.HTTP_403_FORBIDDEN)
    except Exception as e:
        return Response(data={'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
@authentication_classes([CustomAuthBackend])
@transaction.atomic
def remove_podcast_from_playlist(request, playlist_id):
    user_id = request.user.id
    podcast_id = request.data.get('podcast_id')

    try:
        current_playlist: Playlist = Playlist.objects.filter(id=playlist_id) \
            .only('id', 'title', 'owner_id', 'is_private', 'is_required', 'podcast_ids', 'covers',
                  'total_podcast_count').first()

        if current_playlist is None:
            return Response(data={'message': 'Playlist not found'}, status=status.HTTP_404_NOT_FOUND)

        if current_playlist.owner_id != user_id:
            return Response(data={'message': 'User is not the owner'}, status=status.HTTP_403_FORBIDDEN)

        current_playlist.remove_podcast_id_to_playlist(podcast_id)
        return Response(data={'data': PlaylistReadonlySerializer(current_playlist).data},
                        status=status.HTTP_200_OK)
    except Exception as e:
        return Response(data={'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
@authentication_classes([CustomAuthBackend])
@transaction.atomic
def remove_podcast_from_favorite(request):
    user_id = request.user.id
    podcast_id = request.data.get('podcast_id')

    try:
        current_playlist: Playlist = Playlist.objects.filter(title=Playlist.FAVORITE_PLAYLIST_NAME, owner=user_id) \
            .only('id', 'title', 'owner_id', 'is_private', 'podcast_ids', 'covers').first()

        if current_playlist is None:
            current_playlist = create_playlist_by_title(playlist_title=Playlist.FAVORITE_PLAYLIST_NAME, user_id=user_id)

        if current_playlist.owner_id != user_id:
            return Response(data={'message': 'User is not the owner'}, status=status.HTTP_403_FORBIDDEN)

        current_playlist.remove_podcast_id_to_playlist(podcast_id)
        return Response(data={'data': PlaylistReadonlySerializer(current_playlist).data},
                        status=status.HTTP_200_OK)
    except Exception as e:
        return Response(data={'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([CustomAuthBackend])
def get_all_playlists(request):
    user_id = request.user.id

    try:
        playlists = Playlist.objects.filter(owner=user_id, is_required=False) \
            .only('id', 'title', 'owner_id', 'is_required', 'is_private', 'podcast_ids', 'covers')

        return Response(data={'data': PlaylistReadonlySerializer(playlists, many=True).data}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response(data={'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([CustomAuthBackend])
def get_playlist_by_id(request, playlist_id):
    try:
        current_playlist = Playlist.objects.filter(id=playlist_id).only('id', 'title', 'owner_id', 'is_private',
                                                                        'podcast_ids', 'covers', 'is_required').first()

        if current_playlist is None:
            raise ValueError("Playlist not found")

        podcast_episodes = PodcastSeries.objects.filter(id__in=current_playlist.podcast_ids) \
            .only(*['id', 'slug', 'name', 'published_at', 'covers', 'published_episode_count'])

        playlist_data = PlaylistReadonlySerializer(current_playlist).data
        associated_podcast_data = PodcastEpisodeSerializer(podcast_episodes, many=True).data

        return Response(data={'data': {**playlist_data, 'podcasts': associated_podcast_data}},
                        status=status.HTTP_200_OK)
    except Exception as e:
        return Response(data={'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([CustomAuthBackend])
def get_favorite_playlist(request):
    user_id = request.user.id

    try:
        current_playlist = Playlist.objects.filter(title=Playlist.FAVORITE_PLAYLIST_NAME, owner=user_id) \
            .only('id', 'title', 'owner_id', 'is_private', 'podcast_ids', 'covers').first()

        if current_playlist is None:
            current_playlist = create_playlist_by_title(playlist_title=Playlist.FAVORITE_PLAYLIST_NAME, user_id=user_id)

        podcast_episodes = PodcastSeries.objects.filter(id__in=current_playlist.podcast_ids) \
            .only(*['id', 'slug', 'name', 'published_at', 'covers', 'published_episode_count'])

        playlist_data = PlaylistReadonlySerializer(current_playlist).data
        associated_podcast_data = PodcastEpisodeSerializer(podcast_episodes, many=True).data

        return Response(data={'data': {**playlist_data, 'podcasts': associated_podcast_data}},
                        status=status.HTTP_200_OK)
    except Exception as e:
        return Response(data={'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
@authentication_classes([CustomAuthBackend])
def delete_playlist(request, playlist_id):
    try:
        current_playlist: Playlist = Playlist.objects.filter(id=playlist_id) \
            .only('id', 'title', 'owner_id', 'is_private', 'is_required', 'podcast_ids', 'covers').first()

        if current_playlist is None or current_playlist.is_required:
            return Response(data={'message': 'Cannot delete the playlist'}, status=status.HTTP_404_NOT_FOUND)

        current_playlist.delete()

        return Response(data={'message': 'Playlist deleted successfully'}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response(data={'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)


def create_playlist_by_title(playlist_title, user_id):
    return Playlist.objects.create(
        title=playlist_title,
        owner_id=user_id,
        covers=None,
        is_required=True
    )
