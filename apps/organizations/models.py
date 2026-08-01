from django.conf import settings
from django.db import models

from apps.base.models import BaseAuditModel, BaseModel


class Organization(BaseAuditModel):
    """A self-contained tenant with its own members, capital, loans, and contributions."""

    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    is_public = models.BooleanField(default=True)
    # Usable only once the creator's Paystack subscription payment succeeds.
    is_active = models.BooleanField(default=False)

    principal_capital = models.DecimalField(max_digits=14, decimal_places=2, default=0)

    # Org-wide loan settings (Founder-configured; apply to every loan in this org).
    loan_tenure_days = models.PositiveIntegerField(null=True, blank=True)
    interest_rate_percent = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    defaulter_penalty_rate_percent = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    # Org-wide contribution settings (Founder-configured).
    contribution_period_days = models.PositiveIntegerField(null=True, blank=True)
    contribution_amount = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    contribution_fine_enabled = models.BooleanField(default=False)
    contribution_fine_rate_percent = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    contribution_fine_interval_days = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        app_label = 'organizations'

    def __str__(self):
        return self.name


class Membership(BaseModel):
    """Links a user to an organization with a role; also the join-request record while status is pending."""

    FOUNDER = 'founder'
    ADMIN = 'admin'
    MEMBER = 'member'
    ROLE_CHOICES = [
        (FOUNDER, 'Founder'),
        (ADMIN, 'Admin'),
        (MEMBER, 'Member'),
    ]

    PENDING = 'pending'
    APPROVED = 'approved'
    REJECTED = 'rejected'
    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (APPROVED, 'Approved'),
        (REJECTED, 'Rejected'),
    ]

    organization = models.ForeignKey(Organization, related_name='memberships', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='memberships', on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default=MEMBER)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=APPROVED)

    class Meta:
        app_label = 'organizations'
        constraints = [
            models.UniqueConstraint(fields=['organization', 'user'], name='unique_membership_per_org'),
            models.UniqueConstraint(
                fields=['organization'],
                condition=models.Q(role='founder'),
                name='unique_founder_per_org',
            ),
        ]

    def __str__(self):
        return f'{self.user} - {self.organization} ({self.role})'


class Subscription(BaseModel):
    """An Organization's recurring ₦2,000/month Paystack subscription."""

    PENDING = 'pending'
    ACTIVE = 'active'
    GRACE_PERIOD = 'grace_period'
    EXPIRED = 'expired'
    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (ACTIVE, 'Active'),
        (GRACE_PERIOD, 'Grace period'),
        (EXPIRED, 'Expired'),
    ]

    MONTHLY_AMOUNT = 2000

    organization = models.OneToOneField(Organization, related_name='subscription', on_delete=models.CASCADE)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default=PENDING)
    current_period_end = models.DateTimeField(null=True, blank=True)
    grace_period_ends_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        app_label = 'organizations'

    def __str__(self):
        return f'{self.organization} subscription ({self.status})'


class SubscriptionPayment(BaseModel):
    """One Paystack transaction attempt (initial or renewal) for a Subscription."""

    INITIAL = 'initial'
    RENEWAL = 'renewal'
    PURPOSE_CHOICES = [
        (INITIAL, 'Initial'),
        (RENEWAL, 'Renewal'),
    ]

    PENDING = 'pending'
    SUCCESS = 'success'
    FAILED = 'failed'
    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (SUCCESS, 'Success'),
        (FAILED, 'Failed'),
    ]

    subscription = models.ForeignKey(Subscription, related_name='payments', on_delete=models.CASCADE)
    paid_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='subscription_payments', on_delete=models.PROTECT)
    reference = models.CharField(max_length=100, unique=True)
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    purpose = models.CharField(max_length=10, choices=PURPOSE_CHOICES, default=INITIAL)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=PENDING)
    raw_response = models.JSONField(null=True, blank=True)

    class Meta:
        app_label = 'organizations'

    def __str__(self):
        return f'{self.reference} ({self.status})'
