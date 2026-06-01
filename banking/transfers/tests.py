"""
transfers/tests.py — Transfer flow, validation, and money conservation tests.
"""

from decimal import Decimal

from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.test import TestCase
from django.urls import reverse

from bank_accounts.models import Account

from .selectors import TRANSACTIONS_PER_PAGE, TransactionFilters, get_transaction_page
from .services import (
    InsufficientFundsError,
    ReceiverNotFoundError,
    SelfTransferError,
    execute_transfer,
)

User = get_user_model()


class TransferServiceTests(TestCase):
    def setUp(self):
        self.alice = User.objects.create_user(
            email="alice@apex.test",
            password="SecurePass123!",
            first_name="Alice",
            last_name="Apex",
        )
        self.bob = User.objects.create_user(
            email="bob@apex.test",
            password="SecurePass123!",
            first_name="Bob",
            last_name="Bank",
        )
        self.alice_account = self.alice.account
        self.bob_account = self.bob.account

    def test_new_accounts_start_with_ten_thousand_ngn(self):
        self.assertEqual(self.alice_account.balance, Decimal("10000.00"))
        self.assertEqual(len(self.alice_account.account_number), 10)

    def test_successful_transfer_updates_balances_and_creates_transaction(self):
        result = execute_transfer(
            self.alice_account,
            self.bob_account.account_number,
            Decimal("1500.00"),
            note="Lunch",
        )
        self.alice_account.refresh_from_db()
        self.bob_account.refresh_from_db()

        self.assertEqual(self.alice_account.balance, Decimal("8500.00"))
        self.assertEqual(self.bob_account.balance, Decimal("11500.00"))
        self.assertTrue(result.transaction.reference.startswith("TXN-"))
        self.assertEqual(result.transaction.amount, Decimal("1500.00"))
        self.assertEqual(result.transaction.note, "Lunch")

    def test_receiver_not_found(self):
        with self.assertRaises(ReceiverNotFoundError):
            execute_transfer(self.alice_account, "0000000000", Decimal("10.00"))

    def test_self_transfer_rejected(self):
        with self.assertRaises(SelfTransferError):
            execute_transfer(
                self.alice_account,
                self.alice_account.account_number,
                Decimal("10.00"),
            )

    def test_insufficient_funds(self):
        with self.assertRaises(InsufficientFundsError) as ctx:
            execute_transfer(
                self.alice_account,
                self.bob_account.account_number,
                Decimal("10000.01"),
            )
        self.assertEqual(ctx.exception.available, Decimal("10000.00"))

    def test_money_conservation_across_system(self):
        before = Account.objects.aggregate(total=Sum("balance"))["total"]
        execute_transfer(
            self.alice_account,
            self.bob_account.account_number,
            Decimal("250.50"),
        )
        after = Account.objects.aggregate(total=Sum("balance"))["total"]
        self.assertEqual(before, after)


class TransferViewTests(TestCase):
    def setUp(self):
        self.sender = User.objects.create_user(
            email="sender@apex.test",
            password="SecurePass123!",
            first_name="Send",
            last_name="Er",
        )
        self.receiver = User.objects.create_user(
            email="receiver@apex.test",
            password="SecurePass123!",
            first_name="Receive",
            last_name="Er",
        )
        self.client.login(email="sender@apex.test", password="SecurePass123!")

    def test_transfer_page_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse("transfer"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response.url)

    def test_successful_post_redirects_with_message(self):
        receiver_number = self.receiver.account.account_number
        response = self.client.post(
            reverse("transfer"),
            {
                "to_account_number": receiver_number,
                "amount": "500.00",
                "note": "Test",
            },
        )
        self.assertRedirects(response, reverse("dashboard"))
        self.sender.account.refresh_from_db()
        self.receiver.account.refresh_from_db()
        self.assertEqual(self.sender.account.balance, Decimal("9500.00"))
        self.assertEqual(self.receiver.account.balance, Decimal("10500.00"))

    def test_self_transfer_shows_error(self):
        own = self.sender.account.account_number
        response = self.client.post(
            reverse("transfer"),
            {"to_account_number": own, "amount": "100.00"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "cannot send money to yourself")

    def test_invalid_account_shows_error(self):
        response = self.client.post(
            reverse("transfer"),
            {"to_account_number": "1234567890", "amount": "50.00"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "recipient account not found")


class TransactionHistoryPhase4Tests(TestCase):
    def setUp(self):
        self.alice = User.objects.create_user(
            email="alice@apex.test",
            password="SecurePass123!",
            first_name="Alice",
            last_name="Apex",
        )
        self.bob = User.objects.create_user(
            email="bob@apex.test",
            password="SecurePass123!",
            first_name="Bob",
            last_name="Bank",
        )
        self.txn = execute_transfer(
            self.alice.account,
            self.bob.account.account_number,
            Decimal("100.00"),
            note="Phase4",
        ).transaction
        self.client.login(email="alice@apex.test", password="SecurePass123!")

    def test_history_shows_own_transaction_with_all_columns(self):
        response = self.client.get(reverse("history"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.txn.reference)
        self.assertContains(response, self.alice.account.account_number)
        self.assertContains(response, self.bob.account.account_number)
        self.assertContains(response, "Outgoing")

    def test_history_newest_first(self):
        newer = execute_transfer(
            self.alice.account,
            self.bob.account.account_number,
            Decimal("50.00"),
        ).transaction
        content = self.client.get(reverse("history")).content.decode()
        self.assertLess(
            content.index(newer.reference),
            content.index(self.txn.reference),
        )

    def test_detail_page_for_own_transaction(self):
        url = reverse("transaction_detail", args=[self.txn.reference])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.txn.reference)
        self.assertContains(response, "Outgoing")

    def test_cannot_view_other_users_transaction_detail(self):
        """User with no role in the transfer gets 404 (not 403 — no information leak)."""
        charlie = User.objects.create_user(
            email="charlie@apex.test",
            password="SecurePass123!",
            first_name="Charlie",
            last_name="Ch",
        )
        self.client.logout()
        self.client.login(email="charlie@apex.test", password="SecurePass123!")
        url = reverse("transaction_detail", args=[self.txn.reference])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_invalid_reference_returns_404(self):
        response = self.client.get(
            reverse("transaction_detail", args=["TXN-NOTREAL000000"])
        )
        self.assertEqual(response.status_code, 404)

    def test_statement_page_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse("statement"))
        self.assertEqual(response.status_code, 302)

    def test_statement_lists_account_holder(self):
        response = self.client.get(reverse("statement"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Alice Apex")
        self.assertContains(response, self.alice.account.account_number)


class VerifyRecipientTests(TestCase):
    def setUp(self):
        self.alice = User.objects.create_user(
            email="alice@apex.test",
            password="SecurePass123!",
            first_name="Alice",
            last_name="Apex",
        )
        self.bob = User.objects.create_user(
            email="bob@apex.test",
            password="SecurePass123!",
            first_name="Bob",
            last_name="Bank",
        )
        self.client.login(email="alice@apex.test", password="SecurePass123!")

    def test_verify_valid_recipient_returns_name_and_bank(self):
        url = reverse("verify_recipient")
        response = self.client.get(
            url, {"account_number": self.bob.account.account_number}
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["verified"])
        self.assertEqual(data["account_holder"], "Bob Bank")
        self.assertEqual(data["bank_name"], "Apex Bank")

    def test_verify_unknown_account(self):
        response = self.client.get(
            reverse("verify_recipient"), {"account_number": "0000000000"}
        )
        data = response.json()
        self.assertEqual(data["status"], "not_found")
        self.assertFalse(data["verified"])

    def test_verify_own_account_rejected(self):
        response = self.client.get(
            reverse("verify_recipient"),
            {"account_number": self.alice.account.account_number},
        )
        data = response.json()
        self.assertEqual(data["status"], "self")
        self.assertFalse(data["verified"])

    def test_verify_requires_login(self):
        self.client.logout()
        response = self.client.get(
            reverse("verify_recipient"),
            {"account_number": self.bob.account.account_number},
        )
        self.assertEqual(response.status_code, 302)


class TransactionAnalysisPhase5Tests(TestCase):
    def setUp(self):
        self.alice = User.objects.create_user(
            email="alice@apex.test",
            password="SecurePass123!",
            first_name="Alice",
            last_name="Apex",
        )
        self.bob = User.objects.create_user(
            email="bob@apex.test",
            password="SecurePass123!",
            first_name="Bob",
            last_name="Bank",
        )
        self.txn1 = execute_transfer(
            self.alice.account,
            self.bob.account.account_number,
            Decimal("200.00"),
        ).transaction
        self.txn2 = execute_transfer(
            self.bob.account,
            self.alice.account.account_number,
            Decimal("75.50"),
        ).transaction
        self.client.login(email="alice@apex.test", password="SecurePass123!")

    def test_search_by_reference(self):
        response = self.client.get(
            reverse("history"), {"reference": self.txn1.reference[:12]}
        )
        self.assertContains(response, self.txn1.reference)
        self.assertNotContains(response, self.txn2.reference)

    def test_search_by_amount(self):
        response = self.client.get(reverse("history"), {"amount": "200.00"})
        self.assertContains(response, self.txn1.reference)
        self.assertNotContains(response, self.txn2.reference)

    def test_search_by_account_number(self):
        response = self.client.get(
            reverse("history"),
            {"account_number": self.bob.account.account_number},
        )
        self.assertContains(response, self.txn1.reference)

    def test_filter_sent_only(self):
        response = self.client.get(reverse("history"), {"direction": "sent"})
        self.assertContains(response, self.txn1.reference)
        self.assertNotContains(response, self.txn2.reference)

    def test_filter_received_only(self):
        response = self.client.get(reverse("history"), {"direction": "received"})
        self.assertContains(response, self.txn2.reference)
        self.assertNotContains(response, self.txn1.reference)

    def test_combined_search_and_filter(self):
        response = self.client.get(
            reverse("history"),
            {
                "direction": "sent",
                "amount": "200.00",
                "reference": self.txn1.reference,
            },
        )
        self.assertContains(response, self.txn1.reference)
        self.assertNotContains(response, self.txn2.reference)

    def test_statement_summary_statistics(self):
        response = self.client.get(reverse("statement"))
        self.assertContains(response, "Total sent")
        self.assertContains(response, "Total received")
        self.assertContains(response, "Current balance")
        self.assertContains(response, "Transactions")

    def test_summary_totals_match_transfers(self):
        filters = TransactionFilters()
        result = get_transaction_page(self.alice.account, filters)
        self.assertEqual(result.summary.total_sent, Decimal("200.00"))
        self.assertEqual(result.summary.total_received, Decimal("75.50"))
        self.assertEqual(result.summary.total_count, 2)

    def test_pagination_limits_page_size(self):
        for i in range(TRANSACTIONS_PER_PAGE + 3):
            execute_transfer(
                self.alice.account,
                self.bob.account.account_number,
                Decimal("1.00"),
            )
        response = self.client.get(reverse("history"))
        self.assertContains(response, "Page 1 of")
        self.assertContains(response, "Next")

    def test_statement_scoped_to_logged_in_account_only(self):
        """A user not involved in a transfer cannot find it via statement search."""
        charlie = User.objects.create_user(
            email="charlie@apex.test",
            password="SecurePass123!",
            first_name="Charlie",
            last_name="Ch",
        )
        self.client.logout()
        self.client.login(email="charlie@apex.test", password="SecurePass123!")
        response = self.client.get(
            reverse("statement"), {"reference": self.txn1.reference}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["summary"].total_count, 0)
        self.assertContains(response, "No transactions in this period")
