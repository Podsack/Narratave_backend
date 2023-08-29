import serpy
from rest_framework import serializers

from mediacontent.models import PodcastEpisode, F
from ..constants import MediaTypes


class PlaybackHistoryRequestSerializer(serializers.Serializer):
    _content_types = MediaTypes.list()
    episode_id = serializers.IntegerField()
    content_progress = serializers.IntegerField()
    content_type = serializers.CharField()

    def validate_content_type(self, value):
        if value not in self._content_types:
            raise serializers.ValidationError(f"Content type be one of: {', '.join(self._content_types)}")
        return value

    def validate_content_progress(self, value):
        if self.initial_data.get('content_type') == MediaTypes.PODCAST.name and value < 15:
            raise serializers.ValidationError("Cannot be saved without minimum progress")

        return value


class PodcastEpisodeSerializer(serpy.Serializer):
    # MODEL_NAME = PodcastEpisode.
    id = serpy.Field()
    audios = serpy.MethodField()
    title = serpy.StrField()
    duration_in_sec = serpy.IntField()
    covers = serpy.MethodField()
    episode_no = serpy.IntField()
    featured_artists = serpy.MethodField()
    series = serpy.MethodField()
    type = serpy.MethodField()

    _include_artist = False
    _include_series = False

    def __init__(self, instance=None, many=False, include_series=None, include_artist=None, **kwargs):
        super().__init__(instance, many, **kwargs)
        self._include_series = include_series
        self._include_artist = include_artist

    def get_covers(self, obj):
        return [{"url": cover["url"], "bg_color": cover["bg_color"], "dimension": cover["dimension"]} for cover in obj.covers]

    def get_audios(self, obj):
        return [{"url": audio["url"], "format": audio["format"]} for audio in
                obj.audio_metadata]

    def get_featured_artists(self, obj):
        if self._include_artist:
            return EpisodeArtistSerializer(obj.featured_artists.all(), many=True).data
        else:
            return None

    def get_series(self, obj):
        if self._include_series:
            return EpisodeSeriesSerializer(obj.podcast_series).data
        else:
            return None

    def get_type(self, _):
        return PodcastEpisode._meta.model_name


class EpisodeArtistSerializer(serpy.Serializer):
    id = serpy.Field()
    name = serpy.MethodField()
    profile_picture = serpy.Field()

    def get_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"


class EpisodeSeriesSerializer(serpy.Serializer):
    id = serpy.Field()
    name = serpy.Field()
    published_episode_count = serpy.Field()
    type = serpy.MethodField()

    def get_type(self, obj):
        return obj._meta.model_name


class PlaybackHistorySerializer(serpy.Serializer):
    content_progress = serpy.IntField()
    last_played_at = serpy.Field()
    content_object = serpy.Field()
    content = serpy.Field()
