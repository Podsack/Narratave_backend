import serpy
from rest_framework import serializers
import asyncio

from mediacontent.models import PodcastEpisode, F
from ..constants import MediaTypes
from ..models import ContentHistory


class PlaybackHistoryRequestSerializer(serializers.Serializer):
    _content_types = MediaTypes.list()
    episode_id = serializers.IntegerField(allow_null=False)
    start = serializers.IntegerField(allow_null=False)
    end = serializers.IntegerField(allow_null=False)
    object_type = serializers.CharField()

    def validate_object_type(self, value):
        if value not in self._content_types:
            raise serializers.ValidationError(f"Content type be one of: {', '.join(self._content_types)}")
        return value

    def validate(self, data):
        start = data.get('start')
        end = data.get('end')

        # Add your custom validation logic here.
        # For example, checking that field1 and field2 meet a certain condition.
        if end - start < 15:
            raise serializers.ValidationError("Total content progress should be atleast 15 seconds")

        return data

    async def async_save(self, **kwargs):
        self.validated_data.pop('object_type')
        episode_id = self.validated_data.pop('episode_id')
        res = await ContentHistory.objects.acreate(object_id=episode_id, **self.validated_data, **kwargs)
        return res


class PodcastEpisodeSerializer(serpy.Serializer):
    id = serpy.Field()
    audios = serpy.MethodField()
    slug = serpy.StrField()
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
    start = serpy.IntField()
    end = serpy.IntField()
    last_played_at = serpy.Field()
    content_object = serpy.Field()
    content = serpy.Field()
