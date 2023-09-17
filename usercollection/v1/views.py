from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError
from django.db import transaction
from django.db.utils import IntegrityError

from functools import reduce

from authentication.customauth import CustomAuthBackend, IsConsumer
from ..models import Playlist
from mediacontent.models import PodcastEpisode
from .serializers import PlaylistWriteSerializer, PlaylistReadonlySerializer, PodcastEpisodeSerializer
from ..utils import add_duration


@api_view(['POST'])
@permission_classes([IsConsumer])
@authentication_classes([CustomAuthBackend])
def create_playlist(request):
    user_id = request.user.id
    podcast_ids = request.data.get('podcast_ids')
    podcast_details_list = PodcastEpisode.objects.filter(id__in=podcast_ids).values('duration_in_sec', 'covers')
    total_time = reduce(add_duration, podcast_details_list, 0)

    playlist_serializer = PlaylistWriteSerializer(
        data={
            **request.data,
            'owner': user_id,
            'covers': podcast_details_list[0]['covers'],
            'total_duration_sec': total_time
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
@permission_classes([IsConsumer])
@authentication_classes([CustomAuthBackend])
def update_playlist(request):
    new_podcast_ids_map = request.data.get('new_podcast_ids_map')

    try:
        Playlist.update_podcast_ids(playlist_podcast_ids_mapping=new_podcast_ids_map)
        return Response(data={'success': True}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response(data={'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@permission_classes([IsConsumer])
@authentication_classes([CustomAuthBackend])
@transaction.atomic
def add_podcast_to_playlist(request, playlist_id):
    user_id = request.user.id
    podcast_id = request.data.get('podcast_id')

    try:
        '''
        Fetch covers and duration to update
        Also check if this episode exists
        '''
        podcast_episode = PodcastEpisode.objects.filter(id=podcast_id).values('duration_in_sec', 'covers').first()

        if podcast_episode is None:
            return Response(data={'message': 'Invalid podcast detail'}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

        current_playlist = Playlist.objects.filter(id=playlist_id).only('id', 'title', 'owner_id', 'is_private',
                                                                        'podcast_ids',
                                                                        'covers', 'total_duration_sec').first()

        if current_playlist is None:
            return Response(data={'message': 'Playlist not found'}, status=status.HTTP_404_NOT_FOUND)

        if current_playlist.owner_id != user_id:
            return Response(data={'message': 'User is not the owner'}, status=status.HTTP_403_FORBIDDEN)

        if current_playlist.podcast_ids is not None and \
                isinstance(current_playlist.podcast_ids, list):
            if podcast_id in current_playlist.podcast_ids:
                return Response(data={'message': 'Podcast is already present in this playlist'},
                                status=status.HTTP_400_BAD_REQUEST)

            current_playlist.podcast_ids.insert(0, podcast_id)
        else:
            current_playlist.podcast_ids = [podcast_id]

        current_playlist.total_duration_sec = current_playlist.total_duration_sec + podcast_episode['duration_in_sec']
        current_playlist.covers = podcast_episode['covers']
        current_playlist.save()

        return Response(data={'data': PlaylistReadonlySerializer(current_playlist).data},
                        status=status.HTTP_200_OK)
    except Exception as e:
        return Response(data={'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@permission_classes([IsConsumer])
@authentication_classes([CustomAuthBackend])
@transaction.atomic
def remove_podcast_from_playlist(request, playlist_id):
    user_id = request.user.id
    podcast_id = request.data.get('podcast_id')

    try:
        '''
        Fetch covers and duration to update
        Also check if this episode exists
        '''
        podcast_episode_to_delete = PodcastEpisode.objects.filter(id=podcast_id).values('duration_in_sec',
                                                                                        'covers').first()

        if podcast_episode_to_delete is None:
            return Response(data={'message': 'Invalid podcast detail'}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

        current_playlist = Playlist.objects.filter(id=playlist_id).only('id', 'title', 'owner_id', 'is_private',
                                                                        'podcast_ids', 'covers',
                                                                        'total_duration_sec').first()

        if current_playlist is None:
            return Response(data={'message': 'Playlist not found'}, status=status.HTTP_404_NOT_FOUND)

        if current_playlist.owner_id != user_id:
            return Response(data={'message': 'User is not the owner'}, status=status.HTTP_403_FORBIDDEN)

        current_last_added_podcast = None
        if current_playlist.podcast_ids is not None and \
                isinstance(current_playlist.podcast_ids, list):
            if podcast_id not in current_playlist.podcast_ids:
                return Response(data={'message': 'Podcast not in this playlist'}, status=status.HTTP_400_BAD_REQUEST)

            if current_playlist.podcast_ids[0] == podcast_id and len(current_playlist.podcast_ids) > 1:
                current_last_added_podcast = current_playlist.podcast_ids[1]

            current_playlist.podcast_ids.remove(podcast_id)
            current_playlist.total_duration_sec = current_playlist.total_duration_sec - podcast_episode_to_delete[
                'duration_in_sec']
        else:
            current_playlist.podcast_ids = []

        if len(current_playlist.podcast_ids) == 0 and current_last_added_podcast is None:
            current_playlist.total_duration_sec = 0
            current_playlist.covers = None
        elif current_last_added_podcast is not None:
            podcast_episode = PodcastEpisode.objects.filter(id=current_last_added_podcast).values('covers').first()
            current_playlist.covers = podcast_episode['covers']

        current_playlist.save()

        return Response(data={'data': PlaylistReadonlySerializer(current_playlist).data},
                        status=status.HTTP_200_OK)
    except Exception as e:
        return Response(data={'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsConsumer])
@authentication_classes([CustomAuthBackend])
def get_all_playlists(request):
    user_id = request.user.id

    try:
        playlists = Playlist.objects.filter(owner=user_id).only('id', 'title', 'owner_id', 'is_private',
                                                                'podcast_ids', 'covers', 'total_duration_sec')

        return Response(data={'data': PlaylistReadonlySerializer(playlists, many=True).data}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response(data={'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsConsumer])
@authentication_classes([CustomAuthBackend])
def get_playlist_by_id(request, playlist_id):
    try:
        current_playlist = Playlist.objects.filter(id=playlist_id).only('id', 'title', 'owner_id', 'is_private',
                                                                'podcast_ids', 'covers', 'total_duration_sec').first()

        if current_playlist is None:
            raise ValueError("Playlist not found")

        podcast_episodes = PodcastEpisode.objects.filter(id__in=current_playlist.podcast_ids).prefetch_related('featured_artists')\
            .only(*['slug', 'title', 'duration_in_sec', 'audio_metadata', 'covers', 'episode_no'])

        playlist_data = PlaylistReadonlySerializer(current_playlist).data
        associated_podcast_data = PodcastEpisodeSerializer(podcast_episodes, many=True).data

        return Response(data={'data': {**playlist_data, 'podcasts': associated_podcast_data}}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response(data={'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)
