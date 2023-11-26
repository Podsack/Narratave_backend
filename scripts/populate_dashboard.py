import os, sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Narratave.settings')
from django.db.models import Q

import django

django.setup()

from mediacontent.constants import SectionEnum
from mediacontent.models import PodcastEpisode, PodcastSeries, Section
from mediacontent.v1.serializers import PodcastSeriesSerializer

import random


def populate_new_release():
    podcast_series = PodcastSeries.objects.distinct().filter(published=True, podcastepisode__published=True) \
        .prefetch_related('podcastepisode_set').order_by('-published_at')[:20]

    serialized_data = PodcastSeriesSerializer(podcast_series, many=True).data
    section, created = Section.objects.update_or_create(
        title=SectionEnum.NEW_RELEASES.value,
        defaults={
            'title': SectionEnum.NEW_RELEASES.value,
            'item_count': min(20, len(serialized_data)),
            'contents': serialized_data,
            'priority': 2
        })


def populate_coming_soon():
    podcast_series = PodcastSeries.objects.distinct().filter(Q(published=False) | Q(podcastepisode__published=False)) \
        .prefetch_related('podcastepisode_set').order_by('-published_at')[:20]

    serialized_data = PodcastSeriesSerializer(podcast_series, many=True).data
    section, created = Section.objects.update_or_create(
        title=SectionEnum.COMING_SOON.value,
        defaults={
            'title': SectionEnum.COMING_SOON.value,
            'item_count': min(20, len(serialized_data)),
            'contents': serialized_data,
            'priority': 3
        })


def populate_history():
    HISTORY_URL = '/v1/playback/histories'
    section, created = Section.objects.update_or_create(
        title=SectionEnum.CONTINUE_WHERE_YOU_LEFT.value,
        defaults={
            'title': SectionEnum.CONTINUE_WHERE_YOU_LEFT.value,
            'item_count': 0,
            'section_url': HISTORY_URL,
            'priority': 1
        })


def run():
    for i in SectionEnum:
        if i == SectionEnum.RECOMMENDED_FOR_YOU:
            populate_recommended_podcast(i.value)
        elif i == SectionEnum.WEEKLY_PICKS:
            populate_recommended_podcast(i.value)
        elif i == SectionEnum.NEW_RELEASES:
            populate_new_release()
        elif i == SectionEnum.COMING_SOON:
            populate_coming_soon()
        elif i == SectionEnum.CONTINUE_WHERE_YOU_LEFT:
            populate_history()


def populate_recommended_podcast(section):
    podcast_series = PodcastSeries.objects.distinct().filter(published=True,
                                                             podcastepisode__published=True).prefetch_related(
        'podcastepisode_set')

    podcast_list = list(podcast_series)
    random.shuffle(podcast_list)
    podcast_list = podcast_list[:20]

    section, created = Section.objects.update_or_create(
        title=section,
        defaults={
            'title': section,
            'item_count': min(20, len(podcast_list)),
            'contents': PodcastSeriesSerializer(podcast_series, many=True).data,
            'priority': 0
        })


if __name__ == "__main__":
    run()
