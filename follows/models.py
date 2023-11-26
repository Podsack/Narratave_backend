from django.db import models, connection
from django.db.models import QuerySet
from authentication.models import User

from uuid import uuid4


class Relation(models.Model):
    id = models.UUIDField(default=uuid4, primary_key=True)
    follower = models.ForeignKey(to=User, related_name="follower", null=False, on_delete=models.DO_NOTHING)
    followee = models.ForeignKey(to=User, related_name="followee", null=False, on_delete=models.DO_NOTHING)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=('follower_id', 'followee_id'), name='follower_followee_idx'),
            models.Index(condition=models.Q(is_active=True), fields=('follower_id', 'updated_at'), name='follower_updated_time_idx')
        ]

    @classmethod
    def update_follow_relation(cls, follower_id, followee_id, follow=True):
        new_id = uuid4()

        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO follows_relation(id, follower_id, followee_id, is_active, created_at, updated_at) " +
                "VALUES(%s,%s,%s,%s,NOW(),NOW()) " +
                "ON CONFLICT(follower_id, followee_id) " +
                "DO UPDATE set follower_id=%s, followee_id=%s, is_active=%s, updated_at=NOW()",
                (new_id, follower_id, followee_id, follow, follower_id, followee_id, follow,))

        return True

    @classmethod
    def find_relations_with_users(cls, user_id, related_user_ids) -> QuerySet:
        relation_object = cls.objects.filter(is_active=False, follower_id=user_id, followee_id__in=[related_user_ids]).only('followee_id', 'is_active',)
        return relation_object

    @classmethod
    def find_relation_with_user(cls, user_id, related_user_id) -> QuerySet:
        relation = cls.objects.filter(follower_id=user_id, followee_id=related_user_id)\
            .only('follower_id', 'followee_id', 'is_active').first()

        return relation

    @classmethod
    def find_related_users(cls, user_id) -> QuerySet:
        return cls.objects.filter(follwer_id=user_id).only('id')

