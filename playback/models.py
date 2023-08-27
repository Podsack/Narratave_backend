from typing import List, Any

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
    def get_histories_by_user(cls, user, months_ago, last_played_time, page_size=20) -> QuerySet:
        current_time = datetime.today()
        last_played = last_played_time or current_time
        months_previous_date = current_time - timedelta(days=(months_ago * 365 / 12))

        return cls.objects.filter(user=user, last_played_at__lt=last_played, last_played_at__gte=months_previous_date) \
                            .order_by("-last_played_at") \
                            .values("content_type", "object_id", "content_progress", "last_played_at")[:page_size]
