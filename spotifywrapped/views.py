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
    """
    Render the user dashboard.

    :param request: The HTTP request object.
    :return: The rendered dashboard.html page.
    """
    return render(request, 'dashboard.html')