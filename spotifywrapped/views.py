"""
Python file that renders the landing page when the website is opened
"""
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.conf import settings
from spotify_app.models import SpotifyProfile


def landing_page(request):
    """
    Opens landing.html
    :param request: get the given html site
    :return: the landing page
    """
    #BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    #print(os.path.join(BASE_DIR, 'templates'))
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

@login_required
def history(request):
    """
    Render the wrapped history page.

    :param request: The HTTP request object.
    :return: The rendered history.html page.
    """
    if not request.user.is_authenticated:
        # Redirect to the dashboard or any other page if the user is not logged in
        return redirect('dashboard')

    profiles = SpotifyProfile.objects.filter(user=request.user)
    return render(request, 'history.html', {'profiles': profiles})

def contact_developers(request):
    """
    Render the contact developers page.

    :param request: The HTTP request object.
    :return: The rendered contact_developers.html page.
    """
    return render(request, 'contact_developers.html')


def submit_feedback(request):
    """
    Function that controls the feedback form in contact developers
    :param request:
    :return:
    """
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')
        email_body = (
            f"Feedback from {name} ({email}):\n\n"
            f"{message}\n\n"
            "You can reply to this email address to follow up."
        )
        try:
            send_mail(
                subject=f"Feedback from {name}",
                message=email_body,
                from_email=email,
                recipient_list=[settings.CONTACT_EMAIL],
            )
        finally:
            pass
    return redirect('contact_developers')
