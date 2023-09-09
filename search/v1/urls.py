from django.urls import path
from .views import get_search_tags, search_content

urlpatterns = [
    path('suggestions/', get_search_tags),
    path('', search_content)
]