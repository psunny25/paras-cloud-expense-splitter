from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path("", include("expenses.urls")), #my main app
    path("accounts/", include("accounts.urls")),
]
