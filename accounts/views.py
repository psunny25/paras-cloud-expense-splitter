from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from .models import Profile
from .forms import SignupForm, ProfileForm



class CustomLoginView(LoginView):
    """
    Login view using Django's built-in authentication system.

    We only customise:
    - template name
    - redirect field names (use default LOGIN_REDIRECT_URL from settings)
    """
    template_name = "accounts/login.html"

    # Optional: add Bootstrap classes to the default AuthenticationForm
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields["username"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Username"}
        )
        form.fields["password"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Password"}
        )
        return form


class CustomLogoutView(LogoutView):
    """
    Simple logout view – uses LOGOUT_REDIRECT_URL from settings.
    """
    next_page = reverse_lazy("login")


def signup_view(request):
    """
    Handles user registration.

    - GET: show empty signup form
    - POST: validate input, create User, log them in, redirect to dashboard
    """
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Automatically log the user in after successful signup
            login(request, user)
            return redirect("expense_list")
    else:
        form = SignupForm()

    return render(request, "accounts/signup.html", {"form": form})


@login_required
def profile_view(request):
    """
    Display the user's profile.
    """
    profile = request.user.profile
    return render(request, "accounts/profile.html", {"profile": profile})
   

@login_required
def profile_edit_view(request):
    """
    Edit the user's profile fields.
    """
    profile = request.user.profile

    if request.method == "POST":
        form = ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect("profile")
    else:
        form = ProfileForm(instance=profile)

    return render(request, "accounts/profile_edit.html", {"form": form})
