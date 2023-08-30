from django.urls import path
from .views import retrieve_content_categories, get_dashboard_sections, get_customer_history, get_podcast_series_by_id, \
    get_episodes_by_podcast, get_podcast_episode_by_slug

urlpatterns = [
    path('content-categories/', retrieve_content_categories),
    path('home/sections/', get_dashboard_sections),
    path('recently-played/', get_customer_history),
    path('podcast-series/<int:podcast_series_id>/', get_podcast_series_by_id),
    path('podcast-series/<int:podcast_series_id>/episodes/', get_episodes_by_podcast),
    path('podcast-episode/<str:podcast_episode_slug>/', get_podcast_episode_by_slug),
]