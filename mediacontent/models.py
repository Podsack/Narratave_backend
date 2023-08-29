import logging
import os
import uuid
from django.conf import settings

from enum import Enum
from typing import AnyStr
import datetime

from django.db import models
from django.db.models import F
from django.db.models.functions import Lower
from django.utils.text import slugify

from authentication.models import User

logger = logging.getLogger("PodcastSeries")


class Category(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=50, unique=True, db_index=True)
    display_label = models.TextField(max_length=50)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "category"
        verbose_name_plural = "categories"
        constraints = [
            models.UniqueConstraint(Lower('name'), name='unique_lower_name_category')
        ]

    def __str__(self):
        return f"{self.display_label}"


class Tag(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.CharField(max_length=50, unique=True, db_index=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(Lower('name'), name='unique_lower_name_tag')
        ]

    def __str__(self):
        return f"{self.name}"


class CoverSize(Enum):
    LARGE = 320
    MEDIUM = 160
    THUMB = 64


class Series(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(default='', max_length=128)
    slug = models.SlugField(max_length=128, unique=True)
    description = models.TextField(max_length=255, blank=True, default='')
    covers = models.JSONField(null=True)
    # artist = models.CharField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(to=User, null=True, on_delete=models.SET_NULL)
    published = models.BooleanField(default=False)
    published_at = models.DateTimeField(blank=True, null=True)

    _published = None

    class Meta:
        abstract = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        '''
        self._published = self.published can cause infinite loop when calling only or defer queryset 
        '''
        if 'published' not in self.get_deferred_fields():
            setattr(self, '_published', getattr(self, 'published'))

    def __str__(self):
        return f"{self.name}"

    def save(self, *args, **kwargs):
        if self._published != self.published and self.published:
            self.published_at = datetime.datetime.utcnow()

        self.slug = slugify(self.name)
        super().save(*args, **kwargs)
        self._published = self.published


class PodcastSeries(Series):
    published_episode_count = models.IntegerField(default=0, editable=False)

    @classmethod
    def update_series(cls, podcast_series_id, count_change=None):
        if count_change is not None and podcast_series_id is not None:
            '''
            F is used for lock the row in case of concurrent updates
            '''
            try:
                PodcastSeries.objects.filter(pk=podcast_series_id)\
                    .update(published_episode_count=F('published_episode_count') + count_change)
            except Exception as e:
                logger.exception("Updating series count exception %s", str(e))
            # with transaction.atomic():
            #     podcast_series_record = PodcastSeries.objects.select_for_update().get(pk=podcast_series_id)
            #     podcast_series_record.published_episode_count += count_change
            #     podcast_series_record.save()


# class PodcastEpisodeManager(models.Manager):
#     def get_default_values(self):
#         return self.get_queryset().values('id', 'title', 'audio_data', 'covers', 'episode_no', 'duration_in_sec')


class PodcastEpisode(models.Model):
    id = models.BigAutoField(primary_key=True)
    audio_metadata = models.JSONField(null=True)
    title = models.CharField(max_length=255, null=False)
    slug = models.SlugField(max_length=255, null=False, unique=True)
    episode_no = models.IntegerField(default=1, db_index=True)
    duration_in_sec = models.IntegerField(default=0)
    covers = models.JSONField(null=True)
    featured_artists = models.ManyToManyField(to=User, related_name='featured_artists')
    categories = models.ManyToManyField(to=Category)
    language = models.CharField(max_length=3, db_index=True)
    tags = models.ManyToManyField(to=Tag)
    podcast_series = models.ForeignKey(to=PodcastSeries, on_delete=models.CASCADE, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published = models.BooleanField(default=False)
    published_at = models.DateTimeField(blank=True, null=True)

    _published = None

    class Meta:
        verbose_name = 'podcast_episode'
        verbose_name_plural = 'podcast_episodes'
        constraints = [
            models.UniqueConstraint(
                fields=['podcast_series', 'title'],
                name='unique_podcast_series_episode_idx',
                violation_error_message="Title should be unique for a series")
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        '''
        self._published = self.published can cause infinite loop when calling only or defer queryset 
        '''
        if 'published' not in self.get_deferred_fields():
            setattr(self, '_published', getattr(self, 'published'))

    def __str__(self):
        return self.title

    def save(
            self, force_insert=False, force_update=False, using=None, *args, **kwargs
    ):
        if self.published:
            self.published_at = datetime.datetime.utcnow()

        parent_episode_count = None
        if self.pk is None and self.published:
            parent_episode_count = 1
        elif self.pk is not None and self._published != self.published:
            parent_episode_count = 1 if self.published else -1

        self.slug = slugify(f"{self.podcast_series.name} {self.title}")
        super().save(*args, **kwargs)

        PodcastSeries.update_series(podcast_series_id=self.podcast_series.pk, count_change=parent_episode_count)
        # Repopulate the current values
        self._published = self.published


class Section(models.Model):
    title = models.CharField(max_length=255, null=False, db_index=True)
    item_count = models.IntegerField(default=0)
    # JSON field saved
    contents = models.JSONField(blank=True, null=True)
    # url to fetch content for different section if content is not already present
    section_url = models.CharField(max_length=1000, null=True, blank=True)
    priority = models.IntegerField(default=1)
    active = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.title}"


class FileMetadata:
    size_in_kb = 0
    uuid = None
    path = None
    url = None

    def __init__(self, *args, **kwargs):
        self.uuid = uuid.uuid4()
        if 'size_in_kb' in kwargs:
            self.size_in_kb = kwargs['size_in_kb']

    class Meta:
        abstract = True


class AudioMetadata(FileMetadata):
    format: AnyStr = None

    def __init__(self, bitrate_in_kbps, output_ext, file, obj_type, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if output_ext is not None:
            self.format = f"{output_ext.upper()}_{bitrate_in_kbps}"

        if file is not None:
            directory_path = self.get_directory(obj_type=obj_type)
            os.makedirs(directory_path, exist_ok=True)

            file_path = os.path.join(directory_path, file.name)

            with open(file_path, 'wb') as destination:
                for chunk in file.chunks():
                    destination.write(chunk)

            self.path = file_path
            self.url = self.get_url()

    def get_directory(self, obj_type):
        output_path = os.path.join(settings.MEDIA_ROOT, obj_type, "audios", self.format, str(self.uuid))
        return output_path

    def get_url(self):
        url = os.path.join(settings.BASE_DIR, self.path)
        return url


class ImageMetadata(FileMetadata):
    dimension: AnyStr = None
    bg_color = None
    mime_type = None

    def __init__(self, dimension, file, obj_type, mime_type, bg_color, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.bg_color = bg_color
        self.mime_type = mime_type

        if dimension is not None:
            self.dimension = dimension

        if file is not None:
            directory_path = self.get_directory(obj_type=obj_type)
            os.makedirs(directory_path, exist_ok=True)

            file_path = os.path.join(directory_path, file.name)

            with open(file_path, 'wb') as destination:
                for chunk in file.chunks():
                    destination.write(chunk)

            self.path = file_path
            self.url = self.get_url()

    def get_directory(self, obj_type):
        output_path = os.path.join(settings.MEDIA_ROOT, obj_type, "covers", self.dimension, str(self.uuid))
        return output_path

    def get_url(self):
        url = os.path.join(settings.BASE_DIR, self.path)
        return url
