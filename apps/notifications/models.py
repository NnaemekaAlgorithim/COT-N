from django.conf import settings
from django.db import models

from apps.base.models import BaseModel
from apps.organizations.models import Organization


class DeviceToken(BaseModel):
    """An FCM registration token for a user's mobile device."""

    ANDROID = 'android'
    IOS = 'ios'
    PLATFORM_CHOICES = [
        (ANDROID, 'Android'),
        (IOS, 'iOS'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='device_tokens', on_delete=models.CASCADE)
    token = models.CharField(max_length=255, unique=True)
    platform = models.CharField(max_length=10, choices=PLATFORM_CHOICES)
    is_active = models.BooleanField(default=True)

    class Meta:
        app_label = 'notifications'

    def __str__(self):
        return f'{self.user} - {self.platform}'


class Notification(BaseModel):
    """An in-app inbox entry, optionally also pushed to the recipient's devices via FCM."""

    LOAN_REQUEST_SUBMITTED = 'loan_request_submitted'
    LOAN_APPROVED = 'loan_approved'
    LOAN_SENT = 'loan_sent'
    LOAN_REPAYMENT_DUE = 'loan_repayment_due'
    LOAN_REPAYMENT_LOGGED = 'loan_repayment_logged'
    LOAN_OVERDUE = 'loan_overdue'
    CONTRIBUTION_PERIOD_OPENED = 'contribution_period_opened'
    CONTRIBUTION_SUBMITTED = 'contribution_submitted'
    CONTRIBUTION_ACKNOWLEDGED = 'contribution_acknowledged'
    CONTRIBUTION_LATE = 'contribution_late'
    OTHER = 'other'
    TYPE_CHOICES = [
        (LOAN_REQUEST_SUBMITTED, 'Loan request submitted'),
        (LOAN_APPROVED, 'Loan approved'),
        (LOAN_SENT, 'Loan sent'),
        (LOAN_REPAYMENT_DUE, 'Loan repayment due'),
        (LOAN_REPAYMENT_LOGGED, 'Loan repayment logged'),
        (LOAN_OVERDUE, 'Loan overdue'),
        (CONTRIBUTION_PERIOD_OPENED, 'Contribution period opened'),
        (CONTRIBUTION_SUBMITTED, 'Contribution submitted'),
        (CONTRIBUTION_ACKNOWLEDGED, 'Contribution acknowledged'),
        (CONTRIBUTION_LATE, 'Contribution late'),
        (OTHER, 'Other'),
    ]

    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='notifications', on_delete=models.CASCADE)
    organization = models.ForeignKey(
        Organization, related_name='notifications', on_delete=models.CASCADE, null=True, blank=True
    )
    notification_type = models.CharField(max_length=30, choices=TYPE_CHOICES, default=OTHER)
    title = models.CharField(max_length=150)
    body = models.CharField(max_length=500)
    # Extra deep-link context for the mobile app, e.g. {"loan_id": "..."}.
    data = models.JSONField(default=dict, blank=True)
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        app_label = 'notifications'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.recipient} - {self.title}'
