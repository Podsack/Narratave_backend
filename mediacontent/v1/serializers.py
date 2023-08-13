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
        fields = ['display_label', 'name']
        read_only_fields = ('display_label', 'name')


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
    audio_data = serpy.MethodField()
    title = serpy.StrField()
    slug = serpy.StrField()
    description = serpy.StrField()
    duration_in_sec = serpy.IntField()
    covers = serpy.MethodField()
    featured_artists = serpy.MethodField()
    type = serpy.MethodField()

    def get_audio_data(self, obj):
        return AudioDataSerializer(self.audios.all(), many=True).data

    def get_covers(self, obj):
        return CoverArtSerializer(obj.covers.all(), many=True).data

    def get_featured_artists(self, obj):
        return obj.featured_artists.all()

    def get_type(self, obj):
        return obj._meta.model_name


class PodcastSeriesSerializer(serpy.Serializer):
    id = serpy.IntField()
    name = serpy.StrField()
    covers = serpy.MethodField()
    type = serpy.MethodField()

    def get_covers(self, obj):
        return CoverArtSerializer(obj.covers.all(), many=True).data

    def get_type(self, obj):
        return obj._meta.model_name


class PodcastSeriesDetailSerializer(serpy.Serializer):
    id = serpy.IntField()
    name = serpy.StrField()
    covers = serpy.MethodField()
    type = serpy.MethodField()

    def get_covers(self, obj):
        return CoverArtSerializer(obj.covers.all(), many=True).data

    def get_type(self, obj):
        return obj._meta.model_name


class SectionSerializer(serpy.Serializer):
    title = serpy.StrField()
    item_count = serpy.IntField()
    data = serpy.Field(attr="contents")
