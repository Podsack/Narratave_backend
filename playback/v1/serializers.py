import serpy
from rest_framework import serializers

from mediacontent.models import PodcastEpisode
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


class PodcastEpisodeSerializer(serpy.DictSerializer):
    # MODEL_NAME = PodcastEpisode.
    id = serpy.Field()
    audios = serpy.MethodField()
    title = serpy.StrField()
    duration_in_sec = serpy.IntField()
    covers = serpy.MethodField()
    episode_no = serpy.IntField()
    # featured_artists = serpy.MethodField()
    type = serpy.MethodField()

    def get_covers(self, obj):
        return [{"url": cover["url"], "bg_color": cover["bg_color"], "dimension": cover["dimension"]} for cover in obj["covers"]]

    def get_audios(self, obj):
        return [{"url": audio["url"], "format": audio["format"]} for audio in
                obj["audio_metadata"]]

    def get_type(self, _):
        return PodcastEpisode._meta.model_name


class PlaybackHistorySerializer(serpy.Serializer):
    content_progress = serpy.IntField()
    last_played_at = serpy.Field()
    content_object = serpy.Field()
    content = serpy.Field()
