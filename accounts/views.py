from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from .models import Profile
from .forms import SignupForm, ProfileForm



class CustomLoginView(LoginView):
    
    template_name = "accounts/login.html"

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
    
    next_page = reverse_lazy("login")


def signup_view(request):
    
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
    
    profile = request.user.profile
    return render(request, "accounts/profile.html", {"profile": profile})
   

@login_required
def profile_edit_view(request):
    
    profile = request.user.profile

    if request.method == "POST":
        form = ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect("profile")
    else:
        form = ProfileForm(instance=profile)

    return render(request, "accounts/profile_edit.html", {"form": form})
