"""
selectors.py — Read-only queries for transaction history, statements, and analysis.
"""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import Literal

from django.core.paginator import Paginator
from django.db.models import Count, Q, QuerySet, Sum
from django.http import Http404
from django.utils import timezone

from bank_accounts.models import Account

from .models import Transaction

Direction = Literal["sent", "received"]

DIRECTION_OUTGOING = "sent"
DIRECTION_INCOMING = "received"

TYPE_LABELS: dict[Direction, str] = {
    DIRECTION_OUTGOING: "Outgoing",
    DIRECTION_INCOMING: "Incoming",
}

BANK_DISPLAY_NAME = "Apex Bank"
TRANSACTIONS_PER_PAGE = 15

RecipientStatus = Literal["invalid", "not_found", "self", "found"]


@dataclass(frozen=True)
class TransactionFilters:
    """Combined search and filter parameters (from GET query string)."""

    direction: str = "all"
    reference: str = ""
    amount: str = ""
    account_number: str = ""
    date_from: str = ""
    date_to: str = ""

    @classmethod
    def from_request(cls, request) -> "TransactionFilters":
        reference = request.GET.get("reference", "").strip()
        legacy_q = request.GET.get("q", "").strip()
        return cls(
            direction=request.GET.get("direction", "all"),
            reference=reference or legacy_q,
            amount=request.GET.get("amount", "").strip(),
            account_number=request.GET.get("account_number", "").strip(),
            date_from=request.GET.get("date_from", "").strip(),
            date_to=request.GET.get("date_to", "").strip(),
        )

    def has_active_filters(self) -> bool:
        return any([
            self.direction != "all",
            self.reference,
            self.amount,
            self.account_number,
            self.date_from,
            self.date_to,
        ])

    def query_dict(self) -> dict:
        """Build GET params for pagination links (omit empty values)."""
        result = {}
        if self.direction and self.direction != "all":
            result["direction"] = self.direction
        if self.reference:
            result["reference"] = self.reference
        if self.amount:
            result["amount"] = self.amount
        if self.account_number:
            result["account_number"] = self.account_number
        if self.date_from:
            result["date_from"] = self.date_from
        if self.date_to:
            result["date_to"] = self.date_to
        return result


@dataclass(frozen=True)
class StatementSummary:
    """Aggregates for the filtered transaction set."""

    current_balance: Decimal
    total_sent: Decimal
    total_received: Decimal
    total_count: int
    outgoing_count: int
    incoming_count: int


@dataclass(frozen=True)
class TransactionPage:
    """Paginated transaction list plus summary for history/statement views."""

    rows: list
    page_obj: object
    summary: StatementSummary
    filters: TransactionFilters


@dataclass(frozen=True)
class TransactionRow:
    """One transaction as seen by the account holder."""

    txn: Transaction
    direction: Direction

    @property
    def transaction_type(self) -> str:
        return TYPE_LABELS[self.direction]

    @property
    def is_outgoing(self) -> bool:
        return self.direction == DIRECTION_OUTGOING

    @property
    def counterpart_account(self) -> Account:
        if self.is_outgoing:
            return self.txn.receiver_account
        return self.txn.sender_account


def _base_queryset(account: Account) -> QuerySet[Transaction]:
    return (
        Transaction.objects.filter(
            Q(sender_account=account) | Q(receiver_account=account)
        )
        .select_related(
            "sender_account__user",
            "receiver_account__user",
        )
        .order_by("-created_at")
    )


def _direction_for(txn: Transaction, account: Account) -> Direction:
    if txn.sender_account_id == account.pk:
        return DIRECTION_OUTGOING
    return DIRECTION_INCOMING


def _rows_from_queryset(qs, account: Account) -> list[TransactionRow]:
    return [TransactionRow(txn=t, direction=_direction_for(t, account)) for t in qs]


def apply_transaction_filters(
    account: Account,
    filters: TransactionFilters,
) -> QuerySet[Transaction]:
    """
    Return a queryset scoped to this account with all filters applied at DB level.
    """
    qs = _base_queryset(account)

    if filters.direction == DIRECTION_OUTGOING:
        qs = qs.filter(sender_account=account)
    elif filters.direction == DIRECTION_INCOMING:
        qs = qs.filter(receiver_account=account)

    if filters.reference:
        qs = qs.filter(reference__icontains=filters.reference)

    if filters.amount:
        try:
            amount_value = Decimal(filters.amount)
            qs = qs.filter(amount=amount_value)
        except InvalidOperation:
            qs = qs.none()

    if filters.account_number:
        qs = qs.filter(
            Q(sender_account__account_number__icontains=filters.account_number)
            | Q(receiver_account__account_number__icontains=filters.account_number)
        )

    if filters.date_from:
        try:
            df = datetime.strptime(filters.date_from, "%Y-%m-%d").date()
            qs = qs.filter(created_at__date__gte=df)
        except ValueError:
            pass

    if filters.date_to:
        try:
            dt = datetime.strptime(filters.date_to, "%Y-%m-%d").date()
            qs = qs.filter(created_at__date__lte=dt)
        except ValueError:
            pass

    return qs


def compute_statement_summary(
    account: Account,
    filtered_qs: QuerySet[Transaction],
) -> StatementSummary:
    """Summary statistics for the current filter set."""
    total_count = filtered_qs.count()
    agg_sent = filtered_qs.filter(sender_account=account).aggregate(
        total=Sum("amount"),
        count=Count("id"),
    )
    agg_recv = filtered_qs.filter(receiver_account=account).aggregate(
        total=Sum("amount"),
        count=Count("id"),
    )
    return StatementSummary(
        current_balance=account.balance,
        total_sent=agg_sent["total"] or Decimal("0.00"),
        total_received=agg_recv["total"] or Decimal("0.00"),
        total_count=total_count,
        outgoing_count=agg_sent["count"] or 0,
        incoming_count=agg_recv["count"] or 0,
    )


def get_transaction_page(
    account: Account,
    filters: TransactionFilters,
    page_number: int = 1,
    per_page: int = TRANSACTIONS_PER_PAGE,
) -> TransactionPage:
    """
    Filtered, paginated transactions and summary for history/statement views.
    """
    qs = apply_transaction_filters(account, filters)
    summary = compute_statement_summary(account, qs)
    paginator = Paginator(qs, per_page)
    page_obj = paginator.get_page(page_number)
    rows = _rows_from_queryset(page_obj.object_list, account)
    return TransactionPage(
        rows=rows,
        page_obj=page_obj,
        summary=summary,
        filters=filters,
    )


def get_account_transactions(
    account: Account,
    *,
    direction: str = "all",
    search: str = "",
    date_from: str = "",
    date_to: str = "",
) -> list[TransactionRow]:
    """Backward-compatible helper — returns all matching rows (no pagination)."""
    filters = TransactionFilters(
        direction=direction,
        reference=search,
        date_from=date_from,
        date_to=date_to,
    )
    qs = apply_transaction_filters(account, filters)
    return _rows_from_queryset(qs, account)


def get_recent_transactions(account: Account, limit: int = 5) -> list[TransactionRow]:
    qs = _base_queryset(account)[:limit]
    return _rows_from_queryset(qs, account)


def get_transaction_for_account(account: Account, reference: str) -> TransactionRow:
    try:
        txn = (
            Transaction.objects.select_related(
                "sender_account__user",
                "receiver_account__user",
            )
            .get(reference=reference)
        )
    except Transaction.DoesNotExist as exc:
        raise Http404("Transaction not found.") from exc

    if txn.sender_account_id != account.pk and txn.receiver_account_id != account.pk:
        raise Http404("Transaction not found.")

    return TransactionRow(txn=txn, direction=_direction_for(txn, account))


def statement_period_label(date_from: str, date_to: str) -> str:
    if date_from and date_to:
        return f"{date_from} to {date_to}"
    if date_from:
        return f"From {date_from}"
    if date_to:
        return f"Through {date_to}"
    return f"All activity · generated {timezone.now().strftime('%b %d, %Y')}"


@dataclass(frozen=True)
class RecipientVerification:
    status: RecipientStatus
    account_number: str
    account_holder: str = ""
    bank_name: str = BANK_DISPLAY_NAME
    message: str = ""

    def to_dict(self) -> dict:
        return {
            "status": self.status,
            "account_number": self.account_number,
            "account_holder": self.account_holder,
            "bank_name": self.bank_name,
            "message": self.message,
            "verified": self.status == "found",
        }


def verify_recipient_account(
    account_number: str,
    sender_account: Account,
) -> RecipientVerification:
    number = (account_number or "").strip()

    if len(number) != 10 or not number.isdigit():
        return RecipientVerification(
            status="invalid",
            account_number=number,
            message="Enter a valid 10-digit account number.",
        )

    try:
        recipient = Account.objects.select_related("user").get(account_number=number)
    except Account.DoesNotExist:
        return RecipientVerification(
            status="not_found",
            account_number=number,
            message="No Apex account found with this number.",
        )

    if recipient.pk == sender_account.pk:
        return RecipientVerification(
            status="self",
            account_number=number,
            account_holder=sender_account.user.get_full_name(),
            message="You cannot send money to your own account.",
        )

    return RecipientVerification(
        status="found",
        account_number=number,
        account_holder=recipient.user.get_full_name(),
        bank_name=BANK_DISPLAY_NAME,
        message="Account verified. You may proceed with the transfer.",
    )
