# Generated by Django 4.1.3 on 2023-08-21 16:20

from django.db import migrations, models
import django.db.models.functions.text
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('mediacontent', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('name', models.CharField(db_index=True, max_length=50, unique=True)),
            ],
        ),
        migrations.AddConstraint(
            model_name='tag',
            constraint=models.UniqueConstraint(django.db.models.functions.text.Lower('name'), name='unique_lower_name_tag'),
        ),
    ]
