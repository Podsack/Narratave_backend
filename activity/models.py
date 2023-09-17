import uuid
from enum import Enum
from datetime import datetime, timedelta, timezone

from django.db import models
from django.db.models import QuerySet
from django.core.exceptions import ValidationError
from authentication.models import User
from mediacontent.models import PodcastEpisode, PodcastSeries


class ActivityTypeEnum(Enum):
    search = "search"
    like = "like"
    subscribe = "subscribe"


def validation_content_type(value):
    if value is not None:
        if value != PodcastEpisode._meta.model_name or value != PodcastSeries._meta.model_name:
            raise ValidationError("Invalid content_type")
    return value


class Log(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    metadata = models.JSONField(null=True)
    activity_type = models.CharField(null=False, max_length=20)
    content_type = models.CharField(null=True, max_length=20, validators=[validation_content_type])
    content_id = models.PositiveIntegerField(null=True)

    timestamp = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(to=User, on_delete=models.DO_NOTHING)

    class Meta:
        verbose_name = "activity_log"
        verbose_name_plural = "activity_logs"
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['activity_type'], name="activity_log_activity_type_idx")
        ]

    @classmethod
    def get_activities_by_user(cls, user_id, months_ago: int, last_played_time: str, page_size: str | int = 20, activity_type: str=None) -> QuerySet:
        page_size = page_size or 20
        current_time = datetime.now(timezone.utc)
        last_timestamp = datetime.strptime(last_played_time, "%Y-%m-%dT%H:%M:%S.%fZ") if last_played_time else current_time
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
                activity_type,
                metadata,
                content_id,
                content_type,
                timestamp
            FROM (
              SELECT *,
                     ROW_NUMBER() OVER (PARTITION BY content_id, content_type ORDER BY timestamp DESC) AS rn
              FROM activity_log
              WHERE user_id = %s
              AND activity_type = %s
              AND timestamp <= %s
              AND timestamp >= %s
              limit %s
            ) AS ranked
            WHERE rn = 1
            ORDER BY timestamp DESC; 
        """

        results = cls.objects.raw(query, [user_id, activity_type, last_timestamp, months_previous_date, page_size])

        return results
