from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .forms import SignupForm
from .models import Profile


class ProfileSignalTests(TestCase):
    """
    Ensure that a Profile is automatically created for each new User.
    """

    def test_profile_created_for_new_user(self):
        user = User.objects.create_user(username="tester", password="pass1234")
        # If the signal worked, a profile should exist
        self.assertTrue(Profile.objects.filter(user=user).exists())


class SignupFormTests(TestCase):
    """
    Basic validation tests for the custom signup form.
    """

    def test_unique_email_validation(self):
        User.objects.create_user(
            username="existing",
            password="pass1234",
            email="test@example.com",
        )

        form = SignupForm(
            data={
                "username": "newuser",
                "email": "test@example.com",  # same email as existing user
                "password1": "ComplexPass123",
                "password2": "ComplexPass123",
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)


class AuthFlowTests(TestCase):
    """
    Simple test to check signup + login flow via views.
    """

    def test_signup_creates_user_and_logs_in(self):
        response = self.client.post(
            reverse("signup"),
            data={
                "username": "newuser",
                "email": "new@example.com",
                "password1": "ComplexPass123",
                "password2": "ComplexPass123",
            },
            follow=True,
        )

        # User should exist
        self.assertTrue(User.objects.filter(username="newuser").exists())
        # After signup we expect redirect to expense_list (200 status)
        self.assertEqual(response.status_code, 200)
