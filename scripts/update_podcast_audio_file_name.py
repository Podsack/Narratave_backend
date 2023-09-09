import os, sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Narratave.settings')

import django

django.setup()

from mediacontent.models import PodcastEpisode


def map_audio(audio):
    audio['url'] = '_'.join(audio['url'].split(' '))
    audio['path'] = '_'.join(audio['path'].split(' '))
    return audio


def update_podcast(dry_run=True):
    for podcast in PodcastEpisode.objects.all():
        audios = podcast.audio_metadata
        if audios is not None:
            new_audios = list(map(map_audio, audios))
            if dry_run:
                print(new_audios)
            else:
                podcast.audio_metadata = new_audios
                podcast.save()


if __name__ == "__main__":
    update_podcast(dry_run=False)
