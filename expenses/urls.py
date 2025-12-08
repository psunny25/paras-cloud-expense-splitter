from django.urls import path

from .views import (
    PersonListView,
    PersonCreateView,
    PersonUpdateView,
    PersonDeleteView,
    ExpenseListView,
    ExpenseCreateView,
    ExpenseUpdateView,
    ExpenseDeleteView,
    balance_summary,
    RecentActivityListView,
)

urlpatterns = [
    # People management
    path("friends/", PersonListView.as_view(), name="person_list"),
    path("friends/create/", PersonCreateView.as_view(), name="person_create"),
    path("friends/<int:pk>/edit/", PersonUpdateView.as_view(), name="person_update"),
    path("friends/<int:pk>/delete/", PersonDeleteView.as_view(), name="person_delete"),

    # Expenses
    path("", ExpenseListView.as_view(), name="expense_list"),
    path("create/", ExpenseCreateView.as_view(), name="expense_create"),
    path("<int:pk>/edit/", ExpenseUpdateView.as_view(), name="expense_update"),
    path("<int:pk>/delete/", ExpenseDeleteView.as_view(), name="expense_delete"),

    # Summary
    path("summary/", balance_summary, name="balance_summary"),
    path("activity/", RecentActivityListView.as_view(), name="activity_list"),
]
