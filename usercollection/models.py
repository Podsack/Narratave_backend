from django.db import models

from django.contrib.postgres.fields import ArrayField

from authentication.models import User
from mediacontent.models import PodcastSeries


class Playlist(models.Model):
    id = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length=30, null=False, blank=False)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    podcast_ids = ArrayField(models.PositiveBigIntegerField(), null=True, blank=True, default=list, size=50)
    is_private = models.BooleanField(default=False)
    is_required = models.BooleanField(default=False)
    covers = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    FAVORITE_PLAYLIST_NAME = 'Favorite Podcasts'

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['title', 'owner'],
                name='unique_playlist_per_owner',
                violation_error_message="Playlist already exists"
            ),
        ]

    @classmethod
    def update_podcast_ids(cls, playlist_podcast_ids_mapping=None):
        if playlist_podcast_ids_mapping is None:
            playlist_podcast_ids_mapping = []

        playlist_podcast_ids = []
        for playlist_podcast_obj in playlist_podcast_ids_mapping:
            playlist_podcast_ids.append(playlist_podcast_obj.get('playlist_id'))

        playlists = []
        if len(playlist_podcast_ids) > 0:
            playlists = cls.objects.filter(id__in=playlist_podcast_ids)

        for playlist_idx in range(0, len(playlists)):
            playlist = playlists[playlist_idx]
            playlist.podcast_ids = playlist_podcast_ids_mapping[playlist_idx]['new_podcast_ids']
        cls.objects.bulk_update(playlists, ['podcast_ids'])

        return True

    def add_podcast_id_to_playlist(self, podcast_id):
        """
        Fetch covers and duration to update
        Also check if this episode exists
        """
        podcast_episode = PodcastSeries.objects.filter(id=podcast_id).values('covers').first()

        if podcast_episode is None:
            raise ValueError("Podcast id not found")

        if self.podcast_ids is not None and \
                isinstance(self.podcast_ids, list):
            if podcast_id in self.podcast_ids:
                raise ValueError('Podcast is already present in this playlist')

            self.podcast_ids.insert(0, podcast_id)
        else:
            self.podcast_ids = [podcast_id]

        self.covers = podcast_episode['covers']
        self.save()

    def remove_podcast_id_to_playlist(self, podcast_id):
        """
        Fetch covers and duration to update
        Also check if this episode exists
        """
        podcast_episode_to_delete = PodcastSeries.objects.filter(id=podcast_id).values('covers').first()

        if podcast_episode_to_delete is None:
            raise ValueError('Invalid podcast detail')

        current_last_added_podcast = None

        if self.podcast_ids is not None and \
                isinstance(self.podcast_ids, list):
            if podcast_id not in self.podcast_ids:
                raise ValueError('Podcast not in this playlist')

            if self.podcast_ids[0] == podcast_id and len(self.podcast_ids) > 1:
                current_last_added_podcast = self.podcast_ids[1]

            self.podcast_ids.remove(podcast_id)
        else:
            self.podcast_ids = []

        if len(self.podcast_ids) == 0 and current_last_added_podcast is None:
            self.covers = None
        elif current_last_added_podcast is not None:
            podcast_episode = PodcastSeries.objects.filter(id=current_last_added_podcast).values('covers').first()
            self.covers = podcast_episode['covers']

        self.save()
