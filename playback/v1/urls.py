from django.urls import path
from .views import save_playback_history, get_history_by_user

urlpatterns = [
    path("history/save/", save_playback_history),
    path("histories/", get_history_by_user)
]
