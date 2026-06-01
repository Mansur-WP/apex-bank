"""Ledger audit authorization and accounting tests."""

from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .services import execute_transfer


User = get_user_model()


class LedgerVisibilityTests(TestCase):
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

        self.staff = User.objects.create_user(
            email="admin@apex.test",
            password="SecurePass123!",
            first_name="Admin",
            last_name="Staff",
            is_staff=True,
        )

        # create one transfer to generate ledger entries
        execute_transfer(
            self.alice.account,
            self.bob.account.account_number,
            Decimal("100.00"),
            note="Ledger visibility",
        )

        self.client.login(email="alice@apex.test", password="SecurePass123!")

    def test_user_only_sees_entries_for_their_account(self):
        resp = self.client.get(reverse("my_ledger"))
        self.assertEqual(resp.status_code, 200)
        # should show Alice's account number
        self.assertContains(resp, self.alice.account.account_number)
        # should not show Bob's account number
        self.assertNotContains(resp, self.bob.account.account_number)

    def test_admin_sees_all_ledger_entries(self):
        self.client.logout()
        self.client.login(email="admin@apex.test", password="SecurePass123!")
        resp = self.client.get(reverse("ledger_audit"))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, self.alice.account.account_number)
        self.assertContains(resp, self.bob.account.account_number)

    def test_ledger_audit_requires_staff(self):
        resp = self.client.get(reverse("ledger_audit"))
        # non-staff should get 403
        self.assertIn(resp.status_code, [401, 403])

