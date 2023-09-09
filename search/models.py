from django.db import models
from authentication.models import User
from django.contrib.contenttypes.models import ContentType


# class History(models.Model):
#     id = models.UUIDField(primary_key=True)
#     metadata = models.JSONField()
#     content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
#     object_id = models.PositiveIntegerField()
#
#     searched_at = models.DateTimeField(auto_now=True)
#     user = models.ForeignKey(to=User, on_delete=models.CASCADE)
