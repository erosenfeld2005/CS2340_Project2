"""
Tests for UserAuthentication
"""
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from userAuthentication.models import CustomUser
from .forms import SignupForm
#from django.contrib.messages import get_messages


User = get_user_model()

class UserAuthenticationTests(TestCase):
    """
    Tests for UserAuthentication
    """
    def setUp(self):
        self.username = 'testuser'
        self.email = 'testuser@example.com'
        self.password = 'ppppp123444455555*******'
        self.user = User.objects.create_user(username=self.username,
                                             email=self.email, password=self.password)

    def test_signup_valid(self):
        """Test if a new user can sign up successfully."""
        response = self.client.post(reverse('signup'), {
            'name': "name",
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'ppppp123444455555*******',
            'password2': 'ppppp123444455555*******'
        })
        self.assertEqual(response.status_code, 302)  # Check if redirected
        self.assertTrue(User.objects.filter(username='newuser').exists())  # Check if user exists
        self.assertRedirects(response,
                             reverse('dashboard'))

    def test_signup_invalid(self):
        """Test if signup fails with invalid data."""
        response = self.client.post(reverse('signup'), {
            'name': "name",
            'username': self.username,  # Existing username
            'email': 'invalid_email',  # Invalid email
            'password1': 'password123',
            'password2': 'password456'  # Mismatched passwords
        })
        self.assertEqual(response.status_code, 200)  # Should return to the signup page
        form = response.context['form']
        self.assertFormError(form, 'username', 'A user with that username already exists.')
        self.assertFormError(form, 'email', 'Enter a valid email address.')
        self.assertFormError(form, 'password2', 'The two password fields didn’t match.')

    def test_login_valid(self):
        """Test if a user can log in with valid credentials."""
        response = self.client.post(reverse('login'), {
            'username': self.username,
            'password': self.password
        })
        self.assertEqual(response.status_code, 302)  # Should redirect after successful login
        self.assertRedirects(response,
                          reverse('dashboard'))  # Check if redirected to dashboard page

    def test_login_invalid(self):
        """Test if login fails with invalid credentials."""
        response = self.client.post(reverse('login'), {
            'username': 'wronguser',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 200)  # Should return to the login page
        self.assertContains(response, "Invalid username or password.")  # Check for error message

    def test_login_with_empty_fields(self):
        """Test login with empty username and password fields."""
        response = self.client.post(reverse('login'), {
            'username': '',
            'password': ''
        })
        self.assertEqual(response.status_code, 200)  # Should return to the login page
        form = response.context['form']
        self.assertFormError(form,'username', 'This field is required.')
        self.assertFormError(form,'password', 'This field is required.')

class SignupFormTests(TestCase):
    """
    Tests for SignUp Form
    """

    def test_signup_form_valid(self):
        """
        Test if the signup form is valid
        :return: Whether the signup form is valid
        """
        form_data = {
            'name': "name",
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'ppppp1234444****ddd',
            'password2': 'ppppp1234444****ddd'
        }
        form = SignupForm(data=form_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['username'], 'newuser')
        self.assertEqual(form.cleaned_data['email'], 'newuser@example.com')

    def test_email_required(self):
        """
        test for the email
        :return: If the email works
        """
        form_data = {
            'name': "name",
            'username': 'newuser',
            'email': '',  # No email provided
            'password1': 'password123',
            'password2': 'password123'
        }
        form = SignupForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    def test_passwords_match(self):
        """
        test that the passwords match
        :return: If the passwords match
        """
        form_data = {
            'name': "name",
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'password123',
            'password2': 'differentpassword'  # Passwords do not match
        }
        form = SignupForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)

    def test_username_unique(self):
        """
        Tests that the username is unique
        :return: If the username is unique
        """
        # First, create a user with the same username
        CustomUser.objects.create_user(username='newuser',
                                       email='existinguser@example.com', password='password123')

        form_data = {
            'name': "name",
            'username': 'newuser',  # Same username as the existing user
            'email': 'newuser@example.com',
            'password1': 'password123',
            'password2': 'password123'
        }
        form = SignupForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)

    def test_email_validity(self):
        """
        test that the email is valid
        :return: if the email is valid
        """
        form_data = {
            'name': "name",
            'username': 'newuser',
            'email': 'invalidemail',  # Invalid email format
            'password1': 'password123',
            'password2': 'password123'
        }
        form = SignupForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
