import datetime
from django.core.files import File
from django.core.files.uploadedfile import InMemoryUploadedFile
import uuid

from django.contrib import admin
from django import forms
from django.utils.html import format_html

from typing import List, Tuple

from userprofile.utils.app_language_loader import AppLanguageLoader

from .utils import convert_audio_in_aac, get_segmented_audio, ImageUtil, CloudinaryUpload
from .constants import BITRATE_CHOICES
from .models import Category, PodcastSeries, PodcastEpisode, Tag, Section, AudioMetadata, ImageMetadata, \
    CoverSize
from .v1.serializers import AudioMetaDataSerializer, CoverMetaDataSerializer

default_timezone = "IN"


def lang_choices() -> List[Tuple]:
    app_language_loader = AppLanguageLoader()
    choices = [(item['code'], item['localizedLanguage']) for item in
               app_language_loader.app_languages.get(default_timezone)]
    return [('ANY', 'Various Languages'), *choices]


class MediaCategoryAdmin(admin.ModelAdmin):
    fields = ('name', 'display_label', 'bg_color')
    list_display = ('name', 'display_label', 'created_at', 'updated_at', 'bg_color')
    # list_display = ('name', 'display_label', 'created_at', 'updated_at')
    # list_editable = ('name', 'display_label')


class TagAdmin(admin.ModelAdmin):
    fields = ('id', 'name')
    list_display = ('id', 'name')
    readonly_fields = ['id']

    class Meta:
        model = Tag
        fields = 'name'


class SeriesForm(forms.ModelForm):
    # Add a field to the form to handle the image upload
    image = forms.ImageField(label='Cover Image', required=False)

    class Meta:
        model = PodcastSeries
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        self.image = cleaned_data.get('image')

        return cleaned_data


class PodcastSeriesAdmin(admin.ModelAdmin):
    form = SeriesForm
    exclude = ('covers', 'published_at')
    prepopulated_fields = {'slug': ('name',), }

    def cover_set(self, model):
        covers = model.covers
        urls = []
        if covers is not None:
            urls = [f'<a href={cover["url"]}><div>{cover["dimension"]}</div><img src="{cover["url"]}"/></a>' if cover[
                                                                                                                  "url"] is not None else ''
                    for cover in covers]
        return format_html('<br>'.join(urls))

    list_display = ('id', 'name', 'description', 'published_episode_count', 'cover_set', 'created_at', 'updated_at')

    def save_model(self, request, obj, form, change):
        # Get the value of the extra parameter from the form
        image = form.cleaned_data.get('image')

        # Set the value of the extra parameter in the model instance
        if image is not None:
            covers_list = []
            with ImageUtil(image) as pillow_image:
                bg_color = pillow_image.most_common_used_color()

                for cover_size in CoverSize:
                    width = cover_size.value
                    file, name, content_type, size = pillow_image.image_resized(h=width, w=width)

                    path = f'images/{obj._meta.model_name}/{obj.id}/covers/{cover_size.name}/{uuid.uuid4()}'
                    uploaded_img = CloudinaryUpload().upload_image(file, remote_path=path)
                    img_metadata = ImageMetadata(dimension=cover_size.name, file=file, obj_type=obj._meta.model_name,
                                                 mime_type=content_type, bg_color=bg_color, size_in_kb=size / 1024,
                                                 path=path, url=uploaded_img.url)
                    covers_list.append(img_metadata)
            obj.covers = CoverMetaDataSerializer(covers_list, many=True).data

        obj.save()


class PodcastEpisodeForm(forms.ModelForm):
    # categories_list =  Category.objects.filter(is_active=True)

    image = forms.ImageField(label='Cover Image', required=False)
    audio = forms.FileField(label='audio', required=False)
    language = forms.ChoiceField(choices=lambda: lang_choices())
    tags = forms.CharField(
        max_length=500,  # Set your maximum length here
        widget=forms.TextInput(attrs={'maxlength': 500}),  # Set the max length attribute for the widget
    )
    selected_categories = forms.MultipleChoiceField(
        choices=lambda: [(category.name, category.name) for category in Category.objects.filter(is_active=True)],
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = kwargs.get('instance')
        if instance is not None:
            categories = instance.categories
            self.fields['selected_categories'].initial = categories.split(',') if categories is not None else []

    def clean(self):
        cleaned_data = super().clean()
        self.image = cleaned_data.get('image')
        self.audio = cleaned_data.get('audio')

        return cleaned_data


class PodcastEpisodeAdmin(admin.ModelAdmin):
    form = PodcastEpisodeForm
    exclude = ('duration_in_sec', 'audio_metadata', 'covers', 'categories',)
    ordering = ('created_at',)
    list_filter = ('podcast_series', 'language', 'tags', 'categories',)
    search_fields = ('title',)
    filter_horizontal = ('featured_artists',)
    prepopulated_fields = {'slug': ('title', 'podcast_series',), }

    def cover_set(self, model):
        covers = model.covers
        urls = []
        if covers is not None:
            urls = [
                f'<a href={cover["url"]}><div>{cover["dimension"]}</div><img src="{cover["url"]}"/></a>' if "url" in cover else ''
                for cover in covers]
        return format_html('<br>'.join(urls))

    def audio_set(self, model):
        audios = model.audio_metadata
        urls = []
        if audios is not None:
            urls = [
                f'<div>{audio["format"]} Kbps, size: {audio["size_in_kb"]} KB</div><audio controls preload="none"><source src="{audio["url"]}"/></audio>'
                if "url" in audio and "format" in audio else ''
                for audio in audios]
        return format_html('<br>'.join(urls))

    def duration(self, model):
        return 0 if model.duration_in_sec is None else str(datetime.timedelta(seconds=model.duration_in_sec))

    list_display = (
        'title',
        'duration',
        'episode_no',
        'podcast_series',
        'audio_set',
        'cover_set',
        'language',
        'created_at',
        'updated_at')

    def save_model(self, request, obj, form, change):

        # Get the value of the extra parameter from the form
        image = form.cleaned_data.get('image')
        audio: File = form.cleaned_data.get('audio')
        form_categories = form.cleaned_data.get('selected_categories')
        obj.categories = ','.join(form_categories)
        # Set the value of the extra parameter in the model instance
        obj.image = image

        '''
            Add audio to an episode
        '''
        if audio is not None:
            file_name, curr_audio = get_segmented_audio(audio_file=audio)
            obj.duration_in_sec = curr_audio.duration_seconds

            audio_list = []
            for (b, _) in BITRATE_CHOICES:
                file_size, converted_file, converted_format, audio_duration = convert_audio_in_aac(
                    segmented_audio=curr_audio, bitrate=b, file_name=file_name)
                path = f'files/{obj._meta.model_name}/{obj.id}/audios/{b}/{uuid.uuid4()}'
                uploaded_audio = CloudinaryUpload().upload_audio(file=converted_file, remote_path=path)
                audio_metadata = AudioMetadata(bitrate_in_kbps=b, size_in_kb=file_size, file=converted_file,
                                               output_ext=converted_format, obj_type=obj._meta.model_name, path=path,
                                               url=uploaded_audio.get('url'))
                audio_list.append(audio_metadata)

            obj.audio_metadata = AudioMetaDataSerializer(audio_list, many=True).data

        '''
            Add covers to an episode
        '''
        if image is None:
            if obj.covers is None and obj.podcast_series.covers is not None:
                obj.covers = obj.podcast_series.covers
        else:
            covers_list = []
            with ImageUtil(image) as pillow_image:
                bg_color = pillow_image.most_common_used_color()

                for cover_size in CoverSize:
                    width = cover_size.value
                    file, name, content_type, file_size = pillow_image.image_resized(h=width, w=width)
                    path = f'images/{obj._meta.model_name}/{obj.id}/covers/{cover_size.name}/{uuid.uuid4()}'
                    uploaded_img = CloudinaryUpload().upload_image(file, remote_path=path)
                    # file = InMemoryUploadedFile(file, 'image', name, content_type, dimension, None)
                    img_metadata = ImageMetadata(dimension=cover_size.name, file=file, obj_type=obj._meta.model_name,
                                                 mime_type=content_type, bg_color=bg_color, size_in_kb=file_size / 1024,
                                                 path=path, url=uploaded_img.url)
                    covers_list.append(img_metadata)
            obj.covers = CoverMetaDataSerializer(covers_list, many=True).data

        obj.save()


class SectionAdmin(admin.ModelAdmin):
    fields = ('title', 'item_count', 'contents', 'section_url', 'priority', 'active',)
    list_display = ('title', 'item_count', 'contents', 'section_url', 'priority', 'active')
    # prepopulated_fields = {'slug': ('title',), }


admin.site.register(Section, SectionAdmin)
admin.site.register(PodcastSeries, PodcastSeriesAdmin)
admin.site.register(PodcastEpisode, PodcastEpisodeAdmin)
admin.site.register(Category, MediaCategoryAdmin)
admin.site.register(Tag, TagAdmin)
