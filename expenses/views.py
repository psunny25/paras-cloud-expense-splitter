from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import (
    ListView,
    CreateView,
    UpdateView,
    DeleteView,
)

from .forms import ExpenseForm, PersonForm
from .models import Expense, Person, RecentActivity


def log_activity(user, message: str) -> None:
    
    RecentActivity.objects.create(owner=user, message=message)




class PersonListView(LoginRequiredMixin, ListView):
    
    model = Person
    template_name = "expenses/person_list.html"
    context_object_name = "people"

    def get_queryset(self):
        qs = Person.objects.filter(owner=self.request.user).order_by("name")
        q = self.request.GET.get("q", "").strip()
        if q:
            qs = qs.filter(name__icontains=q)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["query"] = self.request.GET.get("q", "").strip()
        return context



class PersonCreateView(LoginRequiredMixin, CreateView):
    
    model = Person
    form_class = PersonForm
    template_name = "expenses/person_form.html"
    success_url = reverse_lazy("person_list")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        response = super().form_valid(form)
        log_activity(self.request.user, f"Added friend '{form.instance.name}'.")
        return response


class PersonUpdateView(LoginRequiredMixin, UpdateView):
    
    model = Person
    form_class = PersonForm
    template_name = "expenses/person_form.html"
    success_url = reverse_lazy("person_list")

    def get_queryset(self):
        return Person.objects.filter(owner=self.request.user)

    def form_valid(self, form):
        response = super().form_valid(form)
        log_activity(self.request.user, f"Updated friend '{form.instance.name}'.")
        return response


class PersonDeleteView(LoginRequiredMixin, DeleteView):
    
    model = Person
    template_name = "expenses/person_confirm_delete.html"
    success_url = reverse_lazy("person_list")

    def get_queryset(self):
        return Person.objects.filter(owner=self.request.user)

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        name = obj.name
        response = super().delete(request, *args, **kwargs)
        log_activity(request.user, f"Deleted friend '{name}'.")
        return response




class ExpenseListView(LoginRequiredMixin, ListView):
    
    model = Expense
    template_name = "expenses/expense_list.html"
    context_object_name = "expenses"

    def get_queryset(self):
        return (
            Expense.objects.filter(owner=self.request.user)
            .select_related("paid_by")
            .prefetch_related("participants")
            .order_by("-date", "-created_at")
        )


class ExpenseCreateView(LoginRequiredMixin, CreateView):
    
    model = Expense
    form_class = ExpenseForm
    template_name = "expenses/expense_form.html"
    success_url = reverse_lazy("expense_list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.owner = self.request.user
        response = super().form_valid(form)
        log_activity(
            self.request.user,
            f"Added expense '{form.instance.description}' "
            f"for €{form.instance.amount}.",
        )
        return response


class ExpenseUpdateView(LoginRequiredMixin, UpdateView):
    
    model = Expense
    form_class = ExpenseForm
    template_name = "expenses/expense_form.html"
    success_url = reverse_lazy("expense_list")

    def get_queryset(self):
        return Expense.objects.filter(owner=self.request.user)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        response = super().form_valid(form)
        log_activity(
            self.request.user,
            f"Updated expense '{form.instance.description}'.",
        )
        return response


class ExpenseDeleteView(LoginRequiredMixin, DeleteView):
    
    model = Expense
    template_name = "expenses/expense_confirm_delete.html"
    success_url = reverse_lazy("expense_list")

    def get_queryset(self):
        return Expense.objects.filter(owner=self.request.user)

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        name = obj.description
        response = super().delete(request, *args, **kwargs)
        log_activity(request.user, f"Deleted expense '{name}'.")
        return response





@login_required
def balance_summary(request):
    
    people = Person.objects.filter(owner=request.user)
    balances = {person.id: Decimal("0.00") for person in people}

    expenses = (
        Expense.objects.filter(owner=request.user)
        .prefetch_related("participants", "paid_by")
    )

    # Build per person balances
    for expense in expenses:
        share = expense.split_amount_per_person()
        balances[expense.paid_by_id] += expense.amount
        for participant in expense.participants.all():
            balances[participant.id] -= share

    # Prepare list for table view
    balance_list = []
    for person in people:
        bal = balances[person.id].quantize(Decimal("0.01"))
        balance_list.append({"person": person, "balance": bal})

    # Sort biggest creditor at the top
    balance_list.sort(key=lambda item: item["balance"], reverse=True)


    creditors = []  # (person, amount > 0)
    debtors = []    # (person, amount > 0, representing how much they owe)

    for person in people:
        bal = balances[person.id].quantize(Decimal("0.01"))
        if bal > 0:
            creditors.append([person, bal])   # mutable list
        elif bal < 0:
            debtors.append([person, -bal])    # store positive amount owed

    settlements = []
    ci = 0
    di = 0

    # Greedy matching between debtors and creditors
    while di < len(debtors) and ci < len(creditors):
        debtor, d_amount = debtors[di]
        creditor, c_amount = creditors[ci]

        pay = min(d_amount, c_amount)

        settlements.append(
            {
                "from": debtor,
                "to": creditor,
                "amount": pay.quantize(Decimal("0.01")),
            }
        )

        d_amount -= pay
        c_amount -= pay

        if d_amount == 0:
            di += 1
        else:
            debtors[di][1] = d_amount

        if c_amount == 0:
            ci += 1
        else:
            creditors[ci][1] = c_amount

    context = {
        "balance_list": balance_list,
        "settlements": settlements,
    }

    return render(request, "expenses/balance_summary.html", context)





class RecentActivityListView(LoginRequiredMixin, ListView):
    
    model = RecentActivity
    template_name = "expenses/activity_list.html"
    context_object_name = "activities"

    def get_queryset(self):
        return RecentActivity.objects.filter(owner=self.request.user)
