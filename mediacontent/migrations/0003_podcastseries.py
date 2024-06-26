# Generated by Django 4.1.3 on 2023-08-21 16:58

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('mediacontent', '0002_tag_tag_unique_lower_name_tag'),
    ]

    operations = [
        migrations.CreateModel(
            name='PodcastSeries',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(default='', max_length=128)),
                ('slug', models.SlugField(max_length=128, unique=True)),
                ('description', models.TextField(blank=True, default='', max_length=255)),
                ('covers', models.JSONField(null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('published', models.BooleanField(default=False)),
                ('published_at', models.DateTimeField(blank=True, null=True)),
                ('published_episode_count', models.IntegerField(default=0, editable=False)),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
