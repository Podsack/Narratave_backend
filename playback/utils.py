import functools

from django.db.models import QuerySet, Prefetch, F, CharField, Value
from typing import List, Dict, Any

from authentication.models import User
from mediacontent.models import PodcastEpisode, PodcastSeries
from .v1.serializers import PodcastEpisodeSerializer


def get_generic_content_value(model_class, id_list, include_artist=False, include_series=False):
    prefetch_query_mapping = {}

    if model_class is PodcastEpisode:
        only_fields = ['id', 'title', 'duration_in_sec', 'audio_metadata', 'covers', 'episode_no']

        if include_artist:
            prefetch_query_mapping['featured_artists'] = User.objects.only('id', 'first_name', 'last_name', 'profile_picture', 'username')

        if include_series:
            '''
            This field needs to be added to only fields otherwise for all episode the podcast_series will be fetched
            '''
            only_fields.append('podcast_series')
            prefetch_query_mapping['podcast_series'] = PodcastSeries.objects.only('id', 'name', 'published_episode_count')

        prefetches = [Prefetch(prefetch_lookup, queryset=prefetch_query_mapping[prefetch_lookup]) for prefetch_lookup in prefetch_query_mapping]

        podcast_list = PodcastEpisode.objects\
            .filter(id__in=id_list).prefetch_related(*prefetches).only(*only_fields)

        return PodcastEpisodeSerializer(instance=podcast_list, many=True, include_artist=include_artist, include_series=include_series).data
    else:
        return ValueError("Generic model value not found")


def include_content(history_data, model_ids_mapping):
    content_type_id = history_data['content_type']
    object_id = history_data['object_id']
    history_data.pop('content_type')
    history_data.pop('object_id')
    history_data['content'] = model_ids_mapping[content_type_id][object_id]
    return history_data


def transform_history_dict(content_histories: QuerySet, model_ids_mapping: Dict[int, Dict[int, Any]], prev_last_played: Any) -> Dict[str, Any]:
    partial_history_mapper = functools.partial(include_content, model_ids_mapping=model_ids_mapping)
    result = dict()
    result["data"] = list(map(partial_history_mapper, content_histories))
    result["prev_last_played_at"] = prev_last_played
    result["item_count"] = len(content_histories)
    return result

