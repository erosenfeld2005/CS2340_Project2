"""
Python file that renders the landing page when the website is opened
"""
from django.shortcuts import render

def landing_page(request):
    """
    Opens landing.html
    :param request: get the given html site
    :return: the landing page
    """
    return render(request, 'landing.html')

def dashboard(request):
    return render(request, 'dashboard.html')