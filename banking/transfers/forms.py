"""
transfers/forms.py — TransferForm for Phase 3.
"""

from django import forms


class TransferForm(forms.Form):
    to_account_number = forms.CharField(
        label="Recipient account number",
        max_length=10,
        min_length=10,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Enter 10-digit account number",
            "autocomplete": "off",
            "inputmode": "numeric",
            "maxlength": "10",
        }),
    )
    amount = forms.DecimalField(
        label="Amount (NGN)",
        max_digits=12,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            "class": "form-control",
            "placeholder": "0.00",
            "step": "0.01",
            "min": "0.01",
        }),
    )
    note = forms.CharField(
        label="Narration (optional)",
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "What's this transfer for?",
        }),
    )

    def clean_to_account_number(self):
        value = self.cleaned_data["to_account_number"].strip()
        if not value.isdigit():
            raise forms.ValidationError("Account number must contain digits only.")
        return value

    def clean_amount(self):
        amount = self.cleaned_data.get("amount")
        if amount is not None and amount <= 0:
            raise forms.ValidationError("Amount must be greater than zero.")
        return amount
