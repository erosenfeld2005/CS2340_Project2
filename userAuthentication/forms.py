"""
Python file that creates forms
"""
from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import CustomUser

# pylint: disable=R0901
# pylint: disable=R0903
class SignupForm(UserCreationForm):
    """
    Creates the signup form
    """
    email = forms.EmailField(max_length=200, help_text='Required')
    name = forms.CharField(max_length=150, required=True,
                           label = 'First Name',
                           help_text='Required')  # Add name as required

    class Meta:
        """
        Creates the meta for the customUser
        """
        model = CustomUser
        fields = ('username', 'name', 'email', 'password1', 'password2')
