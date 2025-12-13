from decimal import Decimal
from datetime import date

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Person, Expense


class ExpenseModelTests(TestCase):
    

    def setUp(self):
        # Create a user + two friends for test data
        self.user = User.objects.create_user(username="tester", password="pass1234")

        self.friend1 = Person.objects.create(owner=self.user, name="Friend 1")
        self.friend2 = Person.objects.create(owner=self.user, name="Friend 2")

    def test_split_amount_per_person(self):
        
        expense = Expense.objects.create(
            owner=self.user,
            description="Test expense",
            amount=Decimal("10.00"),
            paid_by=self.friend1,
            date=date.today(),
        )
        expense.participants.set([self.friend1, self.friend2])

        share = expense.split_amount_per_person()
        self.assertEqual(share, Decimal("5.00"))


class BalanceSummaryViewTests(TestCase):
    

    def setUp(self):
        self.user = User.objects.create_user(username="tester", password="pass1234")

        self.me = Person.objects.create(owner=self.user, name="tester")
        self.friend = Person.objects.create(owner=self.user, name="Friend")

        # Tester pays €10, shared by both
        expense = Expense.objects.create(
            owner=self.user,
            description="Dinner",
            amount=Decimal("10.00"),
            paid_by=self.me,
            date=date.today(),
        )
        expense.participants.set([self.me, self.friend])

    def test_balance_summary_view_status_code(self):
        self.client.login(username="tester", password="pass1234")
        url = reverse("balance_summary")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_balance_summary_contains_expected_balances(self):
        
        
        self.client.login(username="tester", password="pass1234")
        url = reverse("balance_summary")
        response = self.client.get(url)

        balance_list = response.context["balance_list"]

        # Aggregate balances by person name
        balances = {}
        for item in balance_list:
            name = item["person"].name
            balances.setdefault(name, Decimal("0.00"))
            balances[name] += item["balance"]

        self.assertEqual(balances["tester"], Decimal("5.00"))
        self.assertEqual(balances["Friend"], Decimal("-5.00"))
