# Generated by Django 5.1 on 2024-11-23 22:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('spotify_app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='spotifyprofile',
            name='time_range',
            field=models.CharField(blank=True, default='medium_term', max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='temporaryspotifyprofile',
            name='time_range',
            field=models.CharField(blank=True, default='medium_term', max_length=100, null=True),
        ),
    ]
