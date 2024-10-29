"""
Python file to store the different apps
"""
from django.apps import AppConfig


class SpotifyAppConfig(AppConfig):
    """
    Configures our spotify_app correctly
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'spotify_app'
