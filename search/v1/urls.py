from django.urls import path
from .views import get_search_tags, search_content, save_search_history, get_recent_searches

urlpatterns = [
    path('suggestions/', get_search_tags),
    path('', search_content),
    path('history/log/', save_search_history),
    path('history/', get_recent_searches)
]