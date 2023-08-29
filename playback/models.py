from django.db import models
from django.db.models import QuerySet
from datetime import datetime, timedelta

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model

User = get_user_model()


class ContentHistory(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content_progress = models.IntegerField(default=0)
    last_played_at = models.DateTimeField(auto_now=True, db_index=True)

    class Meta:
        verbose_name = 'content_history'
        verbose_name_plural = 'content_histories'

    @classmethod
    def get_histories_by_user(cls, user, months_ago: int, last_played_time: str, page_size: str | int = 20) -> QuerySet:
        page_size = page_size or 20
        current_time = datetime.today()
        last_played = datetime.strptime(last_played_time, "%Y-%m-%dT%H:%M:%S.%fZ") if last_played_time else current_time
        months_previous_date = current_time - timedelta(days=(months_ago * 365 / 12))

        try:
            page_size = int(page_size)
        except ValueError as e:
            raise ValueError("Page size should be an integer")

        return cls.objects.filter(user=user, last_played_at__lt=last_played, last_played_at__gte=months_previous_date) \
                   .order_by("-last_played_at")[:page_size] \
            .values("content_type", "object_id", "content_progress", "last_played_at")

