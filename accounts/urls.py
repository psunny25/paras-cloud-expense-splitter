from django.urls import path

from .views import ( CustomLoginView, CustomLogoutView, signup_view, 
signup_view, profile_view, profile_edit_view,)


urlpatterns = [
    path("login/", CustomLoginView.as_view(), name="login"),
    path("logout/", CustomLogoutView.as_view(), name="logout"),
    path("signup/", signup_view, name="signup"),
    path("profile/", profile_view, name="profile"),
    path("profile/edit/", profile_edit_view, name="profile_edit"),
]
