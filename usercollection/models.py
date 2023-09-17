from django.db import models

from django.contrib.postgres.fields import ArrayField

from authentication.models import User


class Playlist(models.Model):
    id = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length=30, null=False, blank=False)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    podcast_ids = ArrayField(models.PositiveBigIntegerField(), null=True, blank=True, default=list, size=50)
    is_private = models.BooleanField(default=False)
    total_duration_sec = models.PositiveIntegerField(default=0)
    covers = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['title', 'owner'],
                name='unique_playlist_per_owner',
                violation_error_message="Playlist already exists"
            )
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

    @classmethod
    def add_podcast_to_playlist(cls, user_id, playlist_id, podcast_id, podcast_duration, covers):
        return cls.objects.update()
