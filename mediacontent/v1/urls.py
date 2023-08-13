from django.urls import path
from .views import retrieve_content_categories, get_dashboard_sections, get_customer_history

urlpatterns = [
    path('content-categories/', retrieve_content_categories),
    path('home/sections/', get_dashboard_sections),
    path('recently-played/', get_customer_history)
]