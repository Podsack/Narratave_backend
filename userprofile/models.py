from django.db import models
from django.contrib.postgres.fields import ArrayField
from authentication.models import User


class Preference(models.Model):
    name = "preference"
    verbose_name = "user_preferences"

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    country = models.CharField(default='', max_length=50)
    state = models.CharField(default='', max_length=50)
    preferred_app_language = models.CharField(blank=True, max_length=50, null=True)
    preferred_podcast_languages = ArrayField(models.CharField(max_length=50, blank=True), blank=True, default=list)
    preferred_category_ids = ArrayField(models.IntegerField(blank=True), blank=True, default=list)
    # TODO: add preferred category id

