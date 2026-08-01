from django.conf import settings
from django.db import models

from apps.base.models import BaseModel
from apps.organizations.models import Organization


class Loan(BaseModel):
    """A member's loan request against an Organization's principal capital."""

    PENDING_APPROVAL = 'pending_approval'
    APPROVED = 'approved'
    REJECTED = 'rejected'
    SENT = 'sent'
    RECEIVED = 'received'
    REPAID = 'repaid'
    STATUS_CHOICES = [
        (PENDING_APPROVAL, 'Pending approval'),
        (APPROVED, 'Approved'),
        (REJECTED, 'Rejected'),
        (SENT, 'Sent'),
        (RECEIVED, 'Received'),
        (REPAID, 'Repaid'),
    ]
    # Statuses where the loan still counts as "pending" for the leave-organization rule.
    UNRESOLVED_STATUSES = [PENDING_APPROVAL, APPROVED, SENT, RECEIVED]

    organization = models.ForeignKey(Organization, related_name='loans', on_delete=models.CASCADE)
    borrower = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='loans', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING_APPROVAL)

    # Snapshots of the Organization's loan settings at request time.
    tenure_days = models.PositiveIntegerField()
    interest_rate_percent = models.DecimalField(max_digits=5, decimal_places=2)
    defaulter_penalty_rate_percent = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    approved_at = models.DateTimeField(null=True, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    received_at = models.DateTimeField(null=True, blank=True)
    due_date = models.DateTimeField(null=True, blank=True)
    repaid_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        app_label = 'loans'

    def __str__(self):
        return f'{self.borrower} - {self.organization} ({self.amount})'
