"""
Python file that renders the landing page when the website is opened
"""
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.shortcuts import render, redirect

from spotify_app.models import SpotifyProfile


def landing_page(request):
    """
    Opens landing.html
    :param request: get the given html site
    :return: the landing page
    """
    return render(request, 'landing.html')

@login_required
def dashboard(request):
    """
    Render the user dashboard.

    :param request: The HTTP request object.
    :return: The rendered dashboard.html page.
    """
    return render(request, 'dashboard.html')

def summary(request):
    """
    Render the spotify wrapped summary.

    :param request: The HTTP request object.
    :return: The rendered summary.html page.
    """
    return render(request, 'summary.html')

@login_required
def account_settings(request):
    """
    Render the user account settings.
    :param request: The HTTP request object.
    :return: The rendered account_settings.html page.
    """
    return render(request, 'deletion/account_settings.html')

@login_required
def confirm_delete_account(request):
    """
    Render the user confirm delete account button view.
    :param request: The HTTP request object.
    :return: The rendered confirm page
    """
    return render(request, 'deletion/confirm_delete_account.html')

@login_required
def account_deleted(request):
    """
    View to display a message that the account has been successfully deleted.
    """
    return render(request, 'deletion/account_deleted.html')

@login_required
def delete_account_confirmed(request):
    """
    View to display a page that the account has been successfully deleted.
    :param request: The HTTP request object.
    :return: Either the landing or signup page
    """
    if request.method == 'POST':
        request.user.delete()
        logout(request)
        return redirect('landing')
    return redirect('account_settings')

def history(request):
    """
    Render the wrapped history page.

    :param request: The HTTP request object.
    :return: The rendered history.html page.
    """
    profiles = SpotifyProfile.objects.filter(user=request.user)
    return render(request, 'history.html', {'profiles': profiles})
