import os
from django.core.files import File

from django.contrib import admin
from django import forms
from django.utils.html import format_html

from typing import List, Tuple

from userprofile.utils.app_language_loader import AppLanguageLoader

from .utils import convert_audio_in_aac, get_segmented_audio
from .models import Category, Cover, PodcastSeries, Audio, PodcastEpisode, Tag, Section

app_language_loader = AppLanguageLoader()
default_timezone = "IN"


def lang_choices() -> List[Tuple]:
    choices = [(item['code'], item['localizedLanguage']) for item in
               app_language_loader.app_languages.get(default_timezone)]
    return [('ANY', 'Various Languages'), *choices]


class MediaCategoryAdmin(admin.ModelAdmin):
    fields = ('name', 'display_label')
    list_display = ('name', 'display_label', 'created_at', 'updated_at')
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

    def cover_set(self, model):
        covers = model.covers.all()
        urls = [f'<a href={cover.image.url}><span>{cover.dim}</span><img src={cover.image.url}/></a>' for cover in
                covers]
        return format_html('<br>'.join(urls))

    list_display = ('name', 'cover_set', 'created_at', 'updated_at')

    def save_model(self, request, obj, form, change):
        # Get the value of the extra parameter from the form
        image = form.cleaned_data.get('image')

        # Set the value of the extra parameter in the model instance
        obj.image = image

        # Save the instance to the database
        obj.save()


class PodcastEpisodeForm(forms.ModelForm):
    image = forms.ImageField(label='Cover Image', required=False)
    audio = forms.FileField(label='audio', required=False)
    language = forms.ChoiceField(choices=lang_choices())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in ['tags', 'categories']:
            self.fields[field].required = False

    def clean(self):
        cleaned_data = super().clean()
        self.image = cleaned_data.get('image')
        self.audio = cleaned_data.get('audio')

        return cleaned_data


# class AudioInline(GenericTabularInline):
#     model = Audio
#     readonly_fields = ('id', 'file', 'bit_rate', 'format', 'size_in_kb',)
#     extra = 0
#     max_num=0


class PodcastEpisodeAdmin(admin.ModelAdmin):
    form = PodcastEpisodeForm
    exclude = ('duration_in_sec',)
    ordering = ('created_at',)
    list_filter = ('podcast_series', 'language', 'tags', 'categories',)
    search_fields = ('title',)
    filter_horizontal = ('featured_artists', 'tags', 'categories',)

    def cover_set(self, model):
        covers = model.covers.all()
        urls = [f'<a href={cover.image.url}><img src={cover.image.url}/></a>' for cover in covers]
        return format_html('<br>'.join(urls))

    def audio_set(self, model):
        audios = model.audios.all()
        urls = [f'<div>{audio.bit_rate} Kbps</div><audio controls><source src={audio.file.url}/></audio>' for audio in
                audios]
        return format_html('<br>'.join(urls))

    def duration(self, model):
        return 0 if model.duration_in_sec is None else model.duration_in_sec

    list_display = (
        'title',
        'description',
        'duration',
        'cover_set',
        'audio_set',
        'language',
        'created_at',
        'updated_at')

    def save_model(self, request, obj, form, change):

        # Get the value of the extra parameter from the form
        image = form.cleaned_data.get('image')
        audio = form.cleaned_data.get('audio')
        # Set the value of the extra parameter in the model instance
        obj.image = image

        obj.save()

        if audio is not None:
            file_name, curr_audio = get_segmented_audio(audio_file=audio)
            for (b, _) in Audio.BITRATE_CHOICES:
                file_size, new_audio, converted_format, audio_duration = convert_audio_in_aac(
                    segmented_audio=curr_audio, bitrate=b, file_name=file_name)
                obj.duration_in_sec = audio_duration
                new_audio_file = File(new_audio)
                obj.audios.create(file=new_audio_file, bit_rate=b, format=converted_format, size_in_kb=file_size)


class CoverAdmin(admin.ModelAdmin):
    fields = ('image', 'bg_color', 'dim')

    def bg_color_block(self, model):
        return format_html(f'<strong style="color: {model.bg_color}">{model.bg_color}</strong>')

    list_display = ('id', 'image', 'bg_color_block', 'dim', 'height', 'width', 'content')


class AudioAdmin(admin.ModelAdmin):
    fields = ('file', 'bit_rate')
    list_display = ('id', 'file', 'bit_rate', 'format', 'content_type', 'size_in_kb')

    def save_model(self, request, obj, form, change):
        audio_file = form.cleaned_data['file']
        bit_rate = form.cleaned_data['bit_rate']

        file_name, curr_audio = get_segmented_audio(audio_file=audio_file)
        file_size, new_audio, converted_format, audio_duration = convert_audio_in_aac(segmented_audio=curr_audio,
                                                                                      bitrate=bit_rate,
                                                                                      file_name=file_name)

        obj.file = File(new_audio)
        obj.format = converted_format
        obj.size_in_kb = file_size

        # Save the instance to the database
        obj.save()


class SectionAdmin(admin.ModelAdmin):
    fields = ('title', 'item_count', 'contents', 'section_url', 'priority', 'active')
    list_display = fields


admin.site.register(Section, SectionAdmin)
admin.site.register(Audio, AudioAdmin)
admin.site.register(PodcastSeries, PodcastSeriesAdmin)
admin.site.register(PodcastEpisode, PodcastEpisodeAdmin)
admin.site.register(Cover, CoverAdmin)
admin.site.register(Category, MediaCategoryAdmin)
admin.site.register(Tag, TagAdmin)
