import functools

from django.db.models import F, QuerySet
from typing import List, Dict, Any

from mediacontent.models import PodcastEpisode
from .v1.serializers import PodcastEpisodeSerializer


def get_generic_content_value(model_class, id_list):
    if model_class is PodcastEpisode:
        podcast_list = PodcastEpisode.objects.filter(id__in=id_list).values('id', 'title', 'duration_in_sec',
                                                                            'audio_metadata', 'covers', 'episode_no')

        return PodcastEpisodeSerializer(podcast_list, many=True).data
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

