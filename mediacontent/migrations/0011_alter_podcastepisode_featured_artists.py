# Generated by Django 4.1.3 on 2023-12-13 14:56

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('mediacontent', '0010_category_bg_color'),
    ]

    operations = [
        migrations.AlterField(
            model_name='podcastepisode',
            name='featured_artists',
            field=models.ManyToManyField(related_name='featured_podcasts', to=settings.AUTH_USER_MODEL),
        ),
    ]
