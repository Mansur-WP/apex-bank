"""
transfers/views.py — Transfer and history views for Phase 3.
"""

from datetime import datetime
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.shortcuts import redirect, render
from django.views import View

from bank_accounts.models import Account

from .forms import TransferForm
from .models import Transaction


class TransferView(LoginRequiredMixin, View):
    login_url = "/accounts/login/"
    template_name = "transfers/transfer.html"

    def get(self, request):
        return render(request, self.template_name, {
            "form": TransferForm(),
            "account": request.user.account,
        })

    def post(self, request):
        form = TransferForm(request.POST)
        sender_account = request.user.account

        if not form.is_valid():
            return render(request, self.template_name, {
                "form": form,
                "account": sender_account,
            })

        to_account_number = form.cleaned_data["to_account_number"]
        amount = form.cleaned_data["amount"]
        note = form.cleaned_data.get("note", "")

        # Business rule 1: receiver must exist
        try:
            receiver_account = Account.objects.get(account_number=to_account_number)
        except Account.DoesNotExist:
            form.add_error("to_account_number", "No account found with that number.")
            return render(request, self.template_name, {
                "form": form,
                "account": sender_account,
            })

        # Business rule 2: cannot send to yourself
        if receiver_account.pk == sender_account.pk:
            form.add_error("to_account_number", "You cannot transfer money to your own account.")
            return render(request, self.template_name, {
                "form": form,
                "account": sender_account,
            })

        insufficient = False
        try:
            with transaction.atomic():
                locked = Account.objects.select_for_update().filter(
                    pk__in=[sender_account.pk, receiver_account.pk]
                )
                locked_sender   = locked.get(pk=sender_account.pk)
                locked_receiver = locked.get(pk=receiver_account.pk)

                # Business rule 3: sufficient balance
                if locked_sender.balance - amount < Decimal("0.00"):
                    insufficient = True
                    raise ValueError("insufficient_funds")

                locked_sender.balance   -= amount
                locked_receiver.balance += amount
                locked_sender.save(update_fields=["balance", "updated_at"])
                locked_receiver.save(update_fields=["balance", "updated_at"])

                txn = Transaction.objects.create(
                    sender_account=locked_sender,
                    receiver_account=locked_receiver,
                    amount=amount,
                    note=note,
                )

        except ValueError:
            if insufficient:
                form.add_error(
                    "amount",
                    f"Insufficient funds. Available balance: ${sender_account.balance:,.2f}.",
                )
                return render(request, self.template_name, {
                    "form": form,
                    "account": sender_account,
                })
            raise

        messages.success(
            request,
            f"Transfer of ${amount:,.2f} sent successfully. Reference: {txn.reference}",
        )
        return redirect("dashboard")


class TransactionHistoryView(LoginRequiredMixin, View):
    login_url = "/accounts/login/"
    template_name = "transfers/history.html"

    def get(self, request):
        account = request.user.account
        direction = request.GET.get("direction", "all")
        search    = request.GET.get("q", "").strip()
        date_from = request.GET.get("date_from", "")
        date_to   = request.GET.get("date_to", "")

        if direction == "sent":
            sent_qs     = account.sent_transactions.select_related("receiver_account__user")
            received_qs = []
        elif direction == "received":
            sent_qs     = []
            received_qs = account.received_transactions.select_related("sender_account__user")
        else:
            sent_qs     = account.sent_transactions.select_related("receiver_account__user")
            received_qs = account.received_transactions.select_related("sender_account__user")

        txns = sorted(
            [{"txn": t, "direction": "sent",     "counterpart": t.receiver_account} for t in sent_qs] +
            [{"txn": t, "direction": "received",  "counterpart": t.sender_account}   for t in received_qs],
            key=lambda x: x["txn"].created_at,
            reverse=True,
        )

        if search:
            txns = [
                t for t in txns
                if search.lower() in t["txn"].reference.lower()
                or search in t["counterpart"].account_number
                or (t["txn"].note and search.lower() in t["txn"].note.lower())
            ]

        if date_from:
            try:
                df = datetime.strptime(date_from, "%Y-%m-%d").date()
                txns = [t for t in txns if t["txn"].created_at.date() >= df]
            except ValueError:
                pass

        if date_to:
            try:
                dt = datetime.strptime(date_to, "%Y-%m-%d").date()
                txns = [t for t in txns if t["txn"].created_at.date() <= dt]
            except ValueError:
                pass

        return render(request, self.template_name, {
            "transactions": txns,
            "account": account,
            "direction": direction,
            "search": search,
            "date_from": date_from,
            "date_to": date_to,
            "total_count": len(txns),
        })
