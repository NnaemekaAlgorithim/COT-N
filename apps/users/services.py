import random
import string

from django.core.cache import cache
from django.utils.crypto import get_random_string

from .emails import VerificationEmail
from .models import User

VERIFICATION_CODE_TTL_SECONDS = 300


class VerificationError(Exception):
    pass


def _verification_cache_key(email):
    return f'email_verification_code_{email.lower()}'


def generate_unique_username():
    while True:
        username = get_random_string(8, allowed_chars=string.ascii_lowercase + string.digits)
        if not User.objects.filter(username=username).exists():
            return username


def generate_verification_code():
    return ''.join(random.choices(string.digits, k=6))


def send_verification_code(user):
    code = generate_verification_code()
    cache.set(_verification_cache_key(user.email), code, timeout=VERIFICATION_CODE_TTL_SECONDS)
    VerificationEmail({'user': user, 'verification_code': code}).send([user.email])


def register_user(*, email, password, first_name, last_name):
    user = User.objects.create_user(
        username=generate_unique_username(),
        email=email,
        password=password,
        first_name=first_name,
        last_name=last_name,
        is_active=False,
    )
    send_verification_code(user)
    return user


def resend_verification_code(email):
    user = User.objects.get(email__iexact=email)
    send_verification_code(user)
    return user


def verify_email(*, email, code):
    cache_key = _verification_cache_key(email)
    stored_code = cache.get(cache_key)
    if not stored_code:
        raise VerificationError('No verification code found or it has expired.')
    if code != stored_code:
        raise VerificationError('Invalid verification code.')

    user = User.objects.get(email__iexact=email)
    user.is_active = True
    user.save()
    cache.delete(cache_key)
    return user
