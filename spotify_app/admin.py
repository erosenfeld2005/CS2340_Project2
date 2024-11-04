"""
Python file to register our models into admin
"""
from django.contrib import admin
from .models import SpotifyProfile

# Register your models here.
class SpotifyProfileAdmin(admin.ModelAdmin):
    """
    Class to display spotify profile information on the admin page.
    """
    list_display = ('user',)
    list_filter = ('user',)
    search_fields = ('user__username',)
 #   ordering = ('-created_at',)  # Show most recent wraps first
    readonly_fields = ('top_songs', 'top_five_songs', 'top_five_artists', 'vibe_data', 'genre_data')
    # readonly_fields = ('top_songs', 'top_five_artists', 'vibe_data', 'genre_data')

admin.site.register(SpotifyProfile, SpotifyProfileAdmin)
