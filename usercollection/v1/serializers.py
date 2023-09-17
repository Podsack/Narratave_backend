from rest_framework.serializers import ModelSerializer
import serpy

from ..models import Playlist


class PlaylistWriteSerializer(ModelSerializer):
    class Meta:
        model = Playlist
        fields = ('id', 'title', 'owner', 'is_private', 'podcast_ids', 'covers', 'total_duration_sec', 'is_required')


class PlaylistReadonlySerializer(serpy.Serializer):
    id = serpy.IntField()
    title = serpy.StrField()
    owner_id = serpy.IntField()
    is_private = serpy.BoolField()
    podcast_ids = serpy.Field()
    covers = serpy.MethodField()
    total_duration_sec = serpy.IntField()

    def get_covers(self, obj):
        if obj.covers is not None:
            return [{"url": cover["url"], "bg_color": cover["bg_color"], "dimension": cover["dimension"]} for cover in obj.covers]
        else:
            return []


class EpisodeArtistSerializer(serpy.Serializer):
    id = serpy.IntField()
    name = serpy.MethodField()
    role = serpy.StrField()

    def get_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"


class PodcastEpisodeSerializer(serpy.Serializer):
    audios = serpy.MethodField()
    title = serpy.StrField()
    slug = serpy.StrField()
    duration_in_sec = serpy.IntField()
    covers = serpy.MethodField()
    episode_no = serpy.IntField()
    featured_artists = serpy.MethodField()
    type = serpy.MethodField()

    def get_featured_artists(self, obj):
        return EpisodeArtistSerializer(obj.featured_artists.all(), many=True).data

    def get_covers(self, obj):
        return [{"url": cover["url"], "bg_color": cover["bg_color"], "dimension": cover["dimension"]} for cover in obj.covers]

    def get_audios(self, obj):
        return [{"url": audio["url"], "format": audio["format"]} for audio in
                obj.audio_metadata]

    def get_type(self, obj):
        return obj._meta.model_name

