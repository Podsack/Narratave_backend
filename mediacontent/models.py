import os
import uuid

from enum import Enum

from django.db import models
from django.core.validators import RegexValidator
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.db.models.functions import Lower
from django.utils.text import slugify

from authentication.models import User


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


def cover_upload_dir(instance, file_name):
    return os.path.join("uploads", "covers", instance.content_type.model, str(instance.object_id), str(instance.dim),
                        file_name)


COLOR_CODE_VALIDATOR = RegexValidator(
    regex=r'^#([A-Fa-f0-9]{6})$',
    message='Field must contain only letters and numbers.',
)


class CoverSize(Enum):
    LARGE = 320
    MEDIUM = 160
    THUMB = 64


class Cover(models.Model):
    DIMENSIONS = [('LARGE', '320px'), ('MEDIUM', '160px'), ('THUMB', '64px'), ('ORIGINAL', '')]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    image = models.ImageField(upload_to=cover_upload_dir)
    bg_color = models.CharField(max_length=7, default="#000000", validators=[COLOR_CODE_VALIDATOR])
    dim = models.CharField(max_length=20, choices=DIMENSIONS)
    height = models.SmallIntegerField(default=0)
    width = models.SmallIntegerField(default=0)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.BigIntegerField()
    content = GenericForeignKey('content_type', 'object_id')

    class Meta:
        verbose_name = "cover"
        verbose_name_plural = "covers"
        indexes = [
            models.Index(fields=["content_type", "object_id"])
        ]


class Series(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(default='', max_length=128)
    slug = models.SlugField(max_length=128, unique=True)

    covers = GenericRelation(Cover)
    # artist = models.CharField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(to=User, null=True, on_delete=models.SET_NULL)
    published = models.BooleanField(default=False)

    class Meta:
        abstract = True

    def __str__(self):
        return f"{self.name}"

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class PodcastSeries(Series):
    pass


def audio_upload_dir(instance, file_name):
    if instance.content_type is not None:
        return os.path.join("uploads", "audios", instance.content_type.model, str(instance.object_id), str(instance.bit_rate),
                            str(file_name))
    else:
        return os.path.join("uploads", "audios", str(instance.bit_rate), file_name)


class Audio(models.Model):
    BITRATE_CHOICES = [
        (32, '32 Kbps'),
        (64, '64 Kbps'),
        (128, '128 Kbps'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    file = models.FileField(upload_to=audio_upload_dir)
    bit_rate = models.SmallIntegerField(choices=BITRATE_CHOICES)
    format = models.CharField(default='', max_length=5)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.BigIntegerField(null=True, blank=True)
    size_in_kb = models.DecimalField(decimal_places=2, max_digits=10)
    content = GenericForeignKey('content_type', 'object_id')

    class Meta:
        verbose_name = "audio"
        verbose_name_plural = "audios"
        indexes = [
            models.Index(fields=["content_type", "object_id"])
        ]


class PodcastEpisode(models.Model):
    id = models.BigAutoField(primary_key=True)
    audios = GenericRelation(Audio, related_query_name='audios', null=True)
    title = models.CharField(max_length=255, null=False)
    slug = models.SlugField(max_length=255, null=False, unique=True)
    description = models.TextField(default='')
    duration_in_sec = models.IntegerField(default=0)
    covers = GenericRelation(Cover, null=True, related_name='covers')
    featured_artists = models.ManyToManyField(to=User, related_name='featured_artists')
    categories = models.ManyToManyField(to=Category)
    language = models.CharField(max_length=3, db_index=True)
    tags = models.ManyToManyField(to=Tag)
    podcast_series = models.ForeignKey(to=PodcastSeries, on_delete=models.CASCADE, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published = models.BooleanField(default=False)

    __original_audios = None

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
        self.__original_audios = self.audios

    def __str__(self):
        return self.title

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None, *args, **kwargs
    ):
        if hasattr(self, 'audio') and self.__original_audios is not None:
            for audio in self.__original_audios.all():
                audio.delete()

        self.slug = slugify(f"{self.podcast_series.name} {self.title}")
        super().save(*args, **kwargs)
        self.__original_audios = self.audios


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
