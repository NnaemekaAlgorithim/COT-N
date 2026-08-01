from django.utils import timezone

from apps.organizations.models import Membership

from . import fcm
from .models import DeviceToken, Notification


class NotificationError(Exception):
    pass


def register_device_token(*, user, token, platform):
    DeviceToken.objects.update_or_create(
        token=token, defaults={'user': user, 'platform': platform, 'is_active': True}
    )


def unregister_device_token(*, user, token):
    DeviceToken.objects.filter(user=user, token=token).update(is_active=False)


def _push_to_user(*, user, title, body, data):
    tokens = list(DeviceToken.objects.filter(user=user, is_active=True).values_list('token', flat=True))
    invalid_tokens = fcm.send_push_to_tokens(tokens=tokens, title=title, body=body, data=data)
    if invalid_tokens:
        DeviceToken.objects.filter(token__in=invalid_tokens).update(is_active=False)


def notify_user(*, recipient, title, body, notification_type=Notification.OTHER, organization=None, data=None):
    """Creates the inbox entry and best-effort pushes it to the recipient's devices."""
    notification = Notification.objects.create(
        recipient=recipient,
        organization=organization,
        notification_type=notification_type,
        title=title,
        body=body,
        data=data or {},
    )
    _push_to_user(user=recipient, title=title, body=body, data=data or {})
    return notification


def notify_users(*, recipients, title, body, notification_type=Notification.OTHER, organization=None, data=None):
    return [
        notify_user(
            recipient=recipient,
            title=title,
            body=body,
            notification_type=notification_type,
            organization=organization,
            data=data,
        )
        for recipient in recipients
    ]


def notify_admins_and_founder(
    *, organization, title, body, notification_type=Notification.OTHER, data=None, exclude_user=None
):
    """PRD pattern: notify all Admins, or the Founder alone if there are no Admins yet."""
    admins = Membership.objects.filter(organization=organization, role=Membership.ADMIN, status=Membership.APPROVED)
    if exclude_user:
        admins = admins.exclude(user=exclude_user)
    recipients = [membership.user for membership in admins]

    if not recipients:
        founders = Membership.objects.filter(
            organization=organization, role=Membership.FOUNDER, status=Membership.APPROVED
        )
        if exclude_user:
            founders = founders.exclude(user=exclude_user)
        founder_membership = founders.first()
        if founder_membership:
            recipients = [founder_membership.user]

    return notify_users(
        recipients=recipients, title=title, body=body, notification_type=notification_type,
        organization=organization, data=data,
    )


def mark_as_read(*, user, notification):
    if notification.recipient_id != user.id:
        raise NotificationError('This notification does not belong to you.')
    if not notification.is_read:
        notification.is_read = True
        notification.read_at = timezone.now()
        notification.save()
    return notification


def mark_all_as_read(*, user):
    Notification.objects.filter(recipient=user, is_read=False).update(is_read=True, read_at=timezone.now())
