"""
transfers/views.py — TransferView for Phase 3.

Why it exists:
    Handles the money transfer flow: render the form (GET), validate it,
    enforce all business rules, execute the transfer atomically (POST).

Business rules enforced here:
    1. Receiver account must exist.
    2. Sender cannot send money to their own account.
    3. Amount must be greater than zero (also checked in the form).
    4. Sender balance cannot go below zero after the transfer.

Why transaction.atomic?
    A transfer touches two rows (sender and receiver balances) and creates
    a third row (Transaction record). If anything fails mid-way — say the
    receiver credit succeeds but a DB error prevents writing the Transaction
    record — we'd have corrupt state: money leaves the sender but no audit
    trail exists. transaction.atomic wraps all three operations in a single
    database transaction. Either all three succeed together, or none of them
    do and every change is rolled back automatically by PostgreSQL.

How balance validation works:
    We use select_for_update() to lock both account rows for the duration
    of the database transaction. This prevents a race condition where two
    concurrent transfers from the same account both read the same balance,
    both decide there's enough money, and both proceed — resulting in a
    negative balance. With select_for_update(), the second concurrent
    request blocks until the first one commits, then reads the updated balance.

    After locking, we compare: if balance - amount < 0, we raise a sentinel
    ValueError and the atomic block rolls back (no money moves).

How money conservation is guaranteed:
    Inside the atomic block:
        sender.balance   -= amount   (debit)
        receiver.balance += amount   (credit)
    The sum of all balances across all accounts is unchanged:
        Σ balances_before == Σ balances_after
    because every subtraction is paired with an equal addition in the same
    atomic transaction. There is no code path that debits without crediting
    or vice versa.
"""

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
    """
    GET  /transfers/  — show the transfer form.
    POST /transfers/  — validate, execute, redirect.
    """

    login_url = "/accounts/login/"
    template_name = "transfers/transfer.html"

    def get(self, request):
        form = TransferForm()
        return render(request, self.template_name, {
            "form": form,
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

        # ── Business rule 1: receiver must exist ─────────────────────────────
        try:
            receiver_account = Account.objects.get(account_number=to_account_number)
        except Account.DoesNotExist:
            form.add_error("to_account_number", "No account found with that number.")
            return render(request, self.template_name, {
                "form": form,
                "account": sender_account,
            })

        # ── Business rule 2: cannot send to yourself ─────────────────────────
        if receiver_account.pk == sender_account.pk:
            form.add_error(
                "to_account_number",
                "You cannot transfer money to your own account.",
            )
            return render(request, self.template_name, {
                "form": form,
                "account": sender_account,
            })

        # ── Execute the transfer atomically ───────────────────────────────────
        insufficient = False
        try:
            with transaction.atomic():
                # Lock both rows to prevent concurrent race conditions.
                # select_for_update() blocks any other transaction that tries
                # to lock the same rows until this one commits or rolls back.
                locked_accounts = Account.objects.select_for_update().filter(
                    pk__in=[sender_account.pk, receiver_account.pk]
                )
                locked_sender   = locked_accounts.get(pk=sender_account.pk)
                locked_receiver = locked_accounts.get(pk=receiver_account.pk)

                # ── Business rule 3: sufficient balance ──────────────────────
                if locked_sender.balance - amount < Decimal("0.00"):
                    insufficient = True
                    raise ValueError("insufficient_funds")

                # ── Debit sender, credit receiver ────────────────────────────
                locked_sender.balance   -= amount
                locked_receiver.balance += amount
                locked_sender.save(update_fields=["balance", "updated_at"])
                locked_receiver.save(update_fields=["balance", "updated_at"])

                # ── Record the transaction ───────────────────────────────────
                txn = Transaction.objects.create(
                    sender_account=locked_sender,
                    receiver_account=locked_receiver,
                    amount=amount,
                )

        except ValueError:
            if insufficient:
                form.add_error(
                    "amount",
                    f"Insufficient funds. "
                    f"Your available balance is ${sender_account.balance:,.2f}.",
                )
                return render(request, self.template_name, {
                    "form": form,
                    "account": sender_account,
                })
            raise  # unexpected — let Django handle it

        messages.success(
            request,
            f"Transfer of ${amount:,.2f} sent successfully. "
            f"Reference: {txn.reference}",
        )
        return redirect("dashboard")
