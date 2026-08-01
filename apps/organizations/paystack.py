import requests
from django.conf import settings


class PaystackError(Exception):
    pass


def _headers():
    return {
        'Authorization': f'Bearer {settings.PAYSTACK_SECRET_KEY}',
        'Content-Type': 'application/json',
    }


def initialize_transaction(*, email, amount_kobo, reference):
    response = requests.post(
        f'{settings.PAYSTACK_BASE_URL}/transaction/initialize',
        headers=_headers(),
        json={'email': email, 'amount': amount_kobo, 'reference': reference},
        timeout=15,
    )
    data = response.json()
    if not response.ok or not data.get('status'):
        raise PaystackError(data.get('message', 'Failed to initialize Paystack transaction.'))
    return data


def verify_transaction(*, reference):
    response = requests.get(
        f'{settings.PAYSTACK_BASE_URL}/transaction/verify/{reference}',
        headers=_headers(),
        timeout=15,
    )
    data = response.json()
    if not response.ok or not data.get('status'):
        raise PaystackError(data.get('message', 'Failed to verify Paystack transaction.'))
    return data
