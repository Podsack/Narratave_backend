from django.urls import path
from .views import retrieve_content_categories

urlpatterns = [
    path('content-categories/', retrieve_content_categories)
]