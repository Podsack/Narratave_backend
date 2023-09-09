import serpy
from mediacontent.models import CoverSize
from rest_framework import serializers
# from ..models import History


class SearchSeriesSerializer(serpy.Serializer):
    name = serpy.StrField()
    published_episode_count = serpy.IntField()
    type = serpy.MethodField()

    def get_type(self, obj):
        return obj._meta.model_name


class SearchContentSerializer(serpy.Serializer):
    id = serpy.IntField()
    title = serpy.StrField()
    published_at = serpy.Field()
    play_count = serpy.IntField()
    episode_no = serpy.IntField()
    thumb_cover = serpy.MethodField()
    podcast_series = SearchSeriesSerializer()
    type = serpy.MethodField()

    def get_thumb_cover(self, obj):
        result_obj = None
        if obj.covers is not None and isinstance(obj.covers, list):
            filter_gen = filter(lambda a: a["dimension"] == CoverSize.THUMB.name, obj.covers)
            result_obj = next(filter_gen, None)

        return result_obj['url'] if 'url' in result_obj else ''

    def get_type(self, obj):
        return obj._meta.model_name


# class PostSearchSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = History
