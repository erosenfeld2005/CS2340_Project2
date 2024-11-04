"""
Spotify App Migrations
Generated by Django 5.1 on 2024-11-04 00:51
"""

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    """
    Spotify App Migrations
    """

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='SpotifyProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True,
                                           serialize=False, verbose_name='ID')),
                ('top_songs', models.JSONField(blank=True, default=list)),
                ('top_five_artists', models.JSONField(blank=True, default=list)),
                ('vibe_data', models.JSONField(blank=True, default=dict)),
                ('genre_data', models.JSONField(blank=True, default=dict)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE,
                                              related_name='spotify_profile',
                                              to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
