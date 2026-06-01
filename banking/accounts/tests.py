"""
accounts/tests.py — Authentication and dashboard access tests.
"""

from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

User = get_user_model()


class AuthFlowTests(TestCase):
    def test_register_login_dashboard_logout(self):
        register_url = reverse("register")
        response = self.client.post(
            register_url,
            {
                "first_name": "Tayo",
                "last_name": "Ade",
                "email": "tayo@apex.test",
                "password1": "SecurePass123!",
                "password2": "SecurePass123!",
            },
        )
        self.assertRedirects(response, reverse("dashboard"))

        user = User.objects.get(email="tayo@apex.test")
        self.assertEqual(user.account.balance, Decimal("10000.00"))

        self.client.logout()
        login_ok = self.client.login(email="tayo@apex.test", password="SecurePass123!")
        self.assertTrue(login_ok)

        dash = self.client.get(reverse("dashboard"))
        self.assertEqual(dash.status_code, 200)
        self.assertContains(dash, "₦10,000.00")

        logout = self.client.post(reverse("logout"))
        self.assertRedirects(logout, "/accounts/login/")

    def test_dashboard_requires_login(self):
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response.url)
