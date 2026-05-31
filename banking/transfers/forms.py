"""
transfers/forms.py — TransferForm for Phase 3.

Why it exists:
    Separating form logic from view logic keeps each file focused.
    The form handles input parsing and basic field-level validation.
    Business rules (receiver must exist, sufficient balance, etc.) live
    in the view where they can access the database and the logged-in user.

Fields:
    to_account_number — 10-digit string identifying the destination account.
    amount            — the amount to send; must be a positive decimal.
"""

from django import forms


class TransferForm(forms.Form):
    to_account_number = forms.CharField(
        label="Recipient account number",
        max_length=10,
        min_length=10,
        widget=forms.TextInput(attrs={
            "class": "form-control form-control-lg",
            "placeholder": "0000 0000 00",
            "autocomplete": "off",
            "inputmode": "numeric",
            "maxlength": "10",
        }),
    )
    amount = forms.DecimalField(
        label="Amount",
        max_digits=12,
        decimal_places=2,
        min_value=None,   # Business-rule minimum (> 0) enforced in the view
        widget=forms.NumberInput(attrs={
            "class": "form-control form-control-lg",
            "placeholder": "0.00",
            "step": "0.01",
            "min": "0.01",
        }),
    )

    def clean_to_account_number(self):
        """Strip whitespace and verify the value is all digits."""
        value = self.cleaned_data["to_account_number"].strip()
        if not value.isdigit():
            raise forms.ValidationError("Account number must contain digits only.")
        return value

    def clean_amount(self):
        """Reject zero or negative amounts at the form level."""
        amount = self.cleaned_data.get("amount")
        if amount is not None and amount <= 0:
            raise forms.ValidationError("Amount must be greater than zero.")
        return amount
