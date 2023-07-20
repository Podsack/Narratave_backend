from django.contrib import admin
from .models import Category


class MediaCategoryAdmin(admin.ModelAdmin):
    fields = ('name', 'display_label')
    list_display = ('name', 'display_label', 'created_at', 'updated_at')

    pass
    # list_display = ('name', 'display_label', 'created_at', 'updated_at')
    # list_editable = ('name', 'display_label')


admin.site.register(Category, MediaCategoryAdmin)
