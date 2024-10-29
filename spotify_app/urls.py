from django.urls import path
from . import views

urlpatterns = [
    path("spotifylogin/", views.spotify_login, name="spotify_login"),
    path("callback/", views.spotify_callback, name="spotify_callback"),
    path('fetch_data/', views.fetch_user_top_data, name='fetch_user_top_data'),  # This is the initial fetch
    path('display_songs/', views.display_top_songs, name='display_top_songs'),  # New display view for songs
    path('display_artists/', views.display_top_artists, name='display_top_artists'),  # New display view for artists
    path('top_genres/', views.determine_top_genre, name='top_genres'),
]
