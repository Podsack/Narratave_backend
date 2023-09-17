from typing import List, Dict, Any
import functools

from django.db.models import QuerySet


def include_content(data, model_ids_mapping):
    history_data = {}
    content_type = data.content_type
    object_id = data.content_id
    history_data['timestamp'] = data.timestamp

    history_data['content'] = model_ids_mapping[content_type][object_id]
    return history_data


def transform_activity_dict(activity_history: QuerySet, model_ids_mapping: Dict[int, Dict[int, Any]], prev_last_played: Any) -> Dict[str, Any]:
    partial_history_mapper = functools.partial(include_content, model_ids_mapping=model_ids_mapping)
    result = dict()
    result["data"] = list(map(partial_history_mapper, activity_history))
    result["prev_last_timestamp"] = prev_last_played
    result["item_count"] = len(activity_history)
    return result
