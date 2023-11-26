from asgiref.sync import sync_to_async
from rest_framework.pagination import CursorPagination

from .serializer import FollowRelationSerializer
from ..models import Relation
from mediacontent.models import PodcastEpisode


class CustomCursorPagination(CursorPagination):
    page_size = 5
    ordering = '-published_at'
    cursor_query_param = 'cursor'


async def follow_user(user_id, followee_id) -> bool:
    if user_id is None:
        raise ValueError("User id cannot null")
    elif followee_id is None or followee_id < 1 or user_id == followee_id:
        raise ValueError("Followee id is not valid")

    await sync_to_async(Relation.update_follow_relation)(follower_id=user_id, followee_id=followee_id, follow=True)

    return True


async def unfollow_user(user_id, followee_id) -> bool:
    if user_id is None:
        raise ValueError("User id cannot null")
    elif followee_id is None or followee_id < 1 or user_id == followee_id:
        raise ValueError("Followee id cannot null")

    await sync_to_async(Relation.update_follow_relation)(follower_id=user_id, followee_id=followee_id, follow=False)

    return True


async def get_follow_relation(user_id, related_user_id):
    if related_user_id is None or related_user_id < 1 or user_id == related_user_id:
        raise ValueError("Followee id cannot null")

    follow_relation = await sync_to_async(Relation.find_relation_with_user)(user_id=user_id, related_user_id=related_user_id)

    if follow_relation is None:
        return {'is_following': False, 'follower_id': user_id, 'followee_id': related_user_id}

    serializer = FollowRelationSerializer(follow_relation)
    return serializer.data


async def find_followed_users_contents(request, user_id):
    related_user_ids = Relation.find_related_users(user_id=user_id).values_list('id')

    paginator = CustomCursorPagination()
    podcasts_queryset = await PodcastEpisode.find_podcast_by_user_ids(user_ids=related_user_ids)
    paginated_data = paginator.paginate_queryset(queryset=podcasts_queryset, request=request)
    return paginated_data
