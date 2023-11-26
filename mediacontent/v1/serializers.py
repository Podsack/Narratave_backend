from rest_framework import serializers

import serpy
import json

from ..models import Category


class JsonFieldSerializer(serpy.Field):
    def to_value(self, value):
        return value

    def to_representation(self, value):
        return json.loads(value)


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'display_label', 'name']
        read_only_fields = ('id', 'display_label', 'name')


class CoverArtSerializer(serpy.Serializer):
    url = serpy.MethodField()
    bg_color = serpy.StrField()
    dimension = serpy.StrField(attr='dim')
    height = serpy.IntField()
    width = serpy.IntField()

    def get_url(self, obj):
        return obj.image.url


class AudioDataSerializer(serpy.Serializer):
    url = serpy.MethodField()
    bit_rate = serpy.StrField()
    format = serpy.StrField()
    content_type = serpy.MethodField()

    def get_content_type(self, obj):
        return obj.content_type.model

    def get_url(self, obj):
        return obj.file.url


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


class EpisodeArtistSerializer(serpy.Serializer):
    id = serpy.IntField()
    name = serpy.MethodField()

    def get_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"


class PodcastSeriesSerializer(serpy.Serializer):
    id = serpy.IntField()
    name = serpy.StrField()
    description = serpy.StrField()
    covers = serpy.MethodField()
    published_episode_count = serpy.IntField()
    type = serpy.MethodField()

    def get_type(self, obj):
        return obj._meta.model_name

    def get_covers(self, obj):
        return [{"url": cover["url"], "bg_color": cover["bg_color"], "dimension": cover["dimension"]} for cover in obj.covers]


class SectionSerializer(serpy.Serializer):
    title = serpy.StrField()
    item_count = serpy.IntField()
    data = serpy.Field(attr="contents")


class AudioMetaDataSerializer(serpy.Serializer):
    size_in_kb = serpy.IntField()
    path = serpy.StrField()
    url = serpy.StrField()
    format = serpy.StrField()


class CoverMetaDataSerializer(serpy.Serializer):
    size_in_kb = serpy.IntField()
    bg_color = serpy.StrField()
    path = serpy.StrField()
    url = serpy.StrField()
    dimension = serpy.StrField()

