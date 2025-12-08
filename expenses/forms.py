from django import forms

from .models import Expense, Person


class PersonForm(forms.ModelForm):
    """
    Form to create/update a Person (Friend) with Bootstrap styling.
    """

    class Meta:
        model = Person
        fields = ["name", "email"]
        widgets = {
            "name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "e.g. Sunny"}
            ),
            "email": forms.EmailInput(
                attrs={"class": "form-control", "placeholder": "Optional email"}
            ),
        }


class ExpenseForm(forms.ModelForm):
    """
    Form to create/update an Expense.

    We inject the current user into the form so that:
    - 'paid_by' and 'participants' only show that user's friends.
    """

    class Meta:
        model = Expense
        fields = ["description", "amount", "paid_by", "participants", "date"]
        widgets = {
            "description": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "e.g. Groceries"}
            ),
            "amount": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.01", "min": "0.01"}
            ),
            "paid_by": forms.Select(attrs={"class": "form-select"}),
            "date": forms.DateInput(
                attrs={"type": "date", "class": "form-control"}
            ),
            # checkboxes for participants
            "participants": forms.CheckboxSelectMultiple(),
        }

    def __init__(self, *args, user=None, **kwargs):
        """
        Accept a 'user' kwarg so we can filter friend lists per user.
        """
        super().__init__(*args, **kwargs)

        if user is not None:
            qs = Person.objects.filter(owner=user).order_by("name")
            self.fields["paid_by"].queryset = qs
            self.fields["participants"].queryset = qs

    def clean(self):
        cleaned_data = super().clean()
        paid_by = cleaned_data.get("paid_by")
        participants = cleaned_data.get("participants")

        # Make sure there is at least one participant
        if not participants or participants.count() == 0:
            self.add_error(
                "participants",
                "Please select at least one participant for this expense.",
            )

        # Ensure the payer is also a participant
        if paid_by and participants and paid_by not in participants:
            self.add_error(
                "participants",
                "The person who paid must also be included in the participants.",
            )

        return cleaned_data
