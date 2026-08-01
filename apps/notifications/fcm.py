import logging

import firebase_admin
from django.conf import settings
from firebase_admin import credentials
from firebase_admin import messaging
from firebase_admin.exceptions import NotFoundError

logger = logging.getLogger(__name__)

_firebase_app = None


def _get_firebase_app():
    global _firebase_app
    if _firebase_app is None:
        if not settings.FIREBASE_CREDENTIALS_PATH:
            raise RuntimeError('FIREBASE_CREDENTIALS_PATH is not configured.')
        cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS_PATH)
        _firebase_app = firebase_admin.initialize_app(cred)
    return _firebase_app


def send_push_to_tokens(*, tokens, title, body, data=None):
    """Best-effort push send: never raises, returns the tokens FCM says are no longer valid."""
    if not tokens:
        return []

    try:
        app = _get_firebase_app()
    except Exception:
        logger.exception('Firebase is not configured; skipping push notification.')
        return []

    message = messaging.MulticastMessage(
        notification=messaging.Notification(title=title, body=body),
        data={key: str(value) for key, value in (data or {}).items()},
        tokens=tokens,
    )

    try:
        response = messaging.send_each_for_multicast(message, app=app)
    except Exception:
        logger.exception('Failed to send push notification via FCM.')
        return []

    invalid_tokens = [
        token
        for token, result in zip(tokens, response.responses)
        if not result.success and isinstance(result.exception, NotFoundError)
    ]
    return invalid_tokens
