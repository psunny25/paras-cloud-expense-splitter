from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Profile


# -----------------------------
# SIGNUP FORM
# -----------------------------
class SignupForm(UserCreationForm):
    """
    Custom signup form that extends Django's built-in UserCreationForm.

    Captures:
    - username
    - email
    - password1
    - password2

    Email is validated to be unique.
    """

    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(
            attrs={"class": "form-control", "placeholder": "you@example.com"}
        ),
    )

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def __init__(self, *args, **kwargs):
        """
        Add Bootstrap classes to all Django default fields.
        """
        super().__init__(*args, **kwargs)

        self.fields["username"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Choose a username"}
        )
        self.fields["password1"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Password"}
        )
        self.fields["password2"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Repeat password"}
        )

    def clean_email(self):
        """
        Ensure the email is not already used by another user.
        """
        email = self.cleaned_data["email"].lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email


# -----------------------------
# PROFILE EDIT FORM
# -----------------------------
class ProfileForm(forms.ModelForm):
    """
    Form that allows users to edit their profile details.

    Fields:
    - full_name
    - phone_number

    These are stored in the Profile model (OneToOne with User).
    """

    class Meta:
        model = Profile
        fields = ["full_name", "phone_number"]
        widgets = {
            "full_name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Your full name"}
            ),
            "phone_number": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Phone number"}
            ),
        }
