from django.db import models
from django.db.models import QuerySet
from datetime import datetime, timedelta, timezone
import uuid

from django.contrib.contenttypes.fields import GenericForeignKey
from django.db.models import Subquery, OuterRef, F
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model

User = get_user_model()


class ContentHistory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    start = models.IntegerField(default=0)
    end = models.IntegerField(default=0)
    last_played_at = models.DateTimeField(auto_now=True, db_index=True)

    class Meta:
        verbose_name = 'content_history'
        verbose_name_plural = 'content_histories'

    @classmethod
    def get_histories_by_user(cls, user_id, months_ago: int, last_played_time: str, page_size: str | int = 20) -> QuerySet:
        page_size = page_size or 20
        current_time = datetime.now(timezone.utc)
        last_played = datetime.strptime(last_played_time, "%Y-%m-%dT%H:%M:%S.%fZ") if last_played_time else current_time
        months_previous_date = current_time - timedelta(days=(months_ago * 365 / 12))

        try:
            page_size = int(page_size)
        except ValueError as e:
            raise ValueError("Page size should be an integer")

        '''
        Limitation with this query is we can't stop fetching duplicates
        '''
        query = """
            SELECT id,
                object_id,
                content_type_id,
                start,
                "end",
                last_played_at
            FROM (
              SELECT *,
                     ROW_NUMBER() OVER (PARTITION BY object_id, content_type_id ORDER BY last_played_at DESC) AS rn
              FROM playback_contenthistory
              WHERE user_id = %s
              AND last_played_at <= %s
              AND last_played_at >= %s
              limit %s
            ) AS ranked
            WHERE rn = 1
            ORDER BY last_played_at DESC; 
        """

        results = cls.objects.raw(query, [user_id, last_played, months_previous_date, page_size])

        return results
