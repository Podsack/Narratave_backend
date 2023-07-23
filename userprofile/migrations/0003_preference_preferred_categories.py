# Generated by Django 4.1.3 on 2023-07-15 14:10

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userprofile', '0002_alter_preference_preferred_app_language_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='preference',
            name='preferred_categories',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(blank=True, max_length=50), blank=True, default=list, size=None),
        ),
    ]