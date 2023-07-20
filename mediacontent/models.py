from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=50, unique=True, db_index=True)
    display_label = models.TextField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "category"
        verbose_name_plural = "categories"
