from django.contrib import admin
from .models import Preference


class UserPreferenceAdmin(admin.ModelAdmin):
    list_display = ('user', 'country', 'state', 'preferred_app_language', 'preferred_podcast_languages', 'preferred_category_ids')


admin.site.register(Preference, UserPreferenceAdmin)
