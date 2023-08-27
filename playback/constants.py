from enum import Enum
from mediacontent.models import PodcastEpisode


class MediaTypes(Enum):
    PODCAST = PodcastEpisode

    @classmethod
    def list(cls):
        return list(map(lambda c: c.name, cls))
