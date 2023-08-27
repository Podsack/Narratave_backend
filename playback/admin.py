from django.contrib import admin
from .models import ContentHistory


class ContentHistoryAdmin(admin.ModelAdmin):
    list_display=('object_id', 'content_object', 'user', 'content_progress', 'last_played_at')
    ordering = ('-last_played_at', )


admin.site.register(ContentHistory, ContentHistoryAdmin)

