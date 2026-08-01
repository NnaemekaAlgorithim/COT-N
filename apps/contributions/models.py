from django.conf import settings
from django.db import models

from apps.base.models import BaseModel
from apps.organizations.models import Organization


class Contribution(BaseModel):
    """A member's contribution toward an Organization's group savings, pending Admin/Founder acknowledgement."""

    IN_PROGRESS = 'in_progress'
    ACKNOWLEDGED = 'acknowledged'
    STATUS_CHOICES = [
        (IN_PROGRESS, 'In progress'),
        (ACKNOWLEDGED, 'Acknowledged'),
    ]

    organization = models.ForeignKey(Organization, related_name='contributions', on_delete=models.CASCADE)
    contributor = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='contributions', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default=IN_PROGRESS)
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    acknowledged_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='acknowledged_contributions',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    class Meta:
        app_label = 'contributions'

    def __str__(self):
        return f'{self.contributor} - {self.organization} ({self.amount})'
