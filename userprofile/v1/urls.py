from django.urls import path
import userprofile.v1.views as v1_views


urlpatterns = [
    path('app-languages/', v1_views.retrieve_app_languages),
    path('', v1_views.update_preferences)
]