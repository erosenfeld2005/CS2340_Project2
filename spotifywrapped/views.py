"""
Python file that renders the landing page when the website is opened
"""
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

def landing_page(request):
    """
    Opens landing.html
    :param request: get the given html site
    :return: the landing page
    """
    return render(request, 'landing.html')

@login_required
def dashboard(request):
    # Retrieve user-specific data to pass to the template
    top_artists = ["Artist 1", "Artist 2", "Artist 3"]  # Replace with actual query
    top_songs = ["Song 1", "Song 2", "Song 3"]  # Replace with actual query
    playlists = ["Playlist 1", "Playlist 2", "Playlist 3"]  # Replace with actual query
    stats = {
        "total_hours": 120,  # Replace with actual data
        "favorite_genre": "Pop"  # Replace with actual data
    }

    context = {
        'top_artists': top_artists,
        'top_songs': top_songs,
        'playlists': playlists,
        'stats': stats,
    }

    return render(request, 'dashboard.html', context)
