# Generated by Django 4.1.3 on 2023-08-17 17:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mediacontent', '0016_podcastepisode_serial_no'),
    ]

    operations = [
        migrations.AddField(
            model_name='podcastseries',
            name='published_episode_count',
            field=models.IntegerField(default=0),
        ),
    ]
