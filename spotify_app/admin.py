"""
Python file to register our models into admin
"""
from django.contrib import admin
from .models import SpotifyProfile

# Register your models here.
class SpotifyProfileAdmin(admin.ModelAdmin):
    list_display = ('user',)
    list_filter = ('user',)
    search_fields = ('user__username',)
 #   ordering = ('-created_at',)  # Show most recent wraps first
    readonly_fields = ('top_songs', 'top_artists_with_images', 'vibe_data', 'genre_data')  # Make these fields read-only

admin.site.register(SpotifyProfile, SpotifyProfileAdmin)
