from django.contrib import admin
from .models import Preference


class UserPreferenceAdmin(admin.ModelAdmin):
    pass
    # list_display = ('user', 'country', 'state', 'preferred_app_language', 'preferred_podcast_languages')


admin.site.register(Preference, UserPreferenceAdmin)
