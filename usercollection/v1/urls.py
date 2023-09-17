from django.urls import path

from ..v1.views import update_playlist, create_playlist, add_podcast_to_playlist, remove_podcast_from_playlist, \
    get_all_playlists, get_playlist_by_id

urlpatterns = [
    path('', get_all_playlists),
    path('<int:playlist_id>/', get_playlist_by_id),
    path('create/', create_playlist),
    path('bulk-update/', update_playlist),
    path('<int:playlist_id>/add-podcast/', add_podcast_to_playlist),
    path('<int:playlist_id>/remove-podcast/', remove_podcast_from_playlist),
]
