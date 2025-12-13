from decimal import Decimal

from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.db import models


class Person(models.Model):
    

    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="friends",
        null=True,
        blank=True,
    )

    name = models.CharField(
        max_length=100,
        help_text="Name of the person in the expense group.",
    )
    email = models.EmailField(
        blank=True,
        null=True,
        help_text="Optional email address (for information only, not for login).",
    )

    def __str__(self):
        
        if self.owner and self.owner.username and self.name == self.owner.username:
            return f"Me ({self.owner.username})"
        return self.name


class Expense(models.Model):
    

    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="expenses",
        null=True,
        blank=True,
    )

    description = models.CharField(
        max_length=200,
        help_text="Short description of what this expense was for.",
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
        help_text="Total expense amount (must be greater than 0).",
    )
    paid_by = models.ForeignKey(
        Person,
        on_delete=models.CASCADE,
        related_name="expenses_paid",
        help_text="Person who actually paid this expense.",
    )
    participants = models.ManyToManyField(
        Person,
        related_name="expenses_participated",
        help_text="People who share this expense. The amount is split equally.",
    )
    date = models.DateField(
        help_text="Date when the expense happened.",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp automatically set when the expense is created.",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp automatically updated when the expense is changed.",
    )

    def __str__(self):
        return f"{self.description} ({self.amount} paid by {self.paid_by})"

    def split_amount_per_person(self) -> Decimal:
        
        count = self.participants.count()
        if count == 0:
            return Decimal("0.00")
        share = self.amount / count
        return share.quantize(Decimal("0.01"))


class RecentActivity(models.Model):
   

    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="activities",
    )
    message = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.created_at:%Y-%m-%d %H:%M} - {self.message}"
