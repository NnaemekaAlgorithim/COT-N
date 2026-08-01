from django.db import transaction
from django.utils import timezone

from apps.base.models import set_current_user
from apps.notifications.models import Notification
from apps.notifications.services import notify_admins_and_founder, notify_user
from apps.organizations.models import Membership, Organization

from .models import Contribution


class ContributionError(Exception):
    pass


def make_contribution(*, user, organization, amount):
    is_member = Membership.objects.filter(organization=organization, user=user, status=Membership.APPROVED).exists()
    if not is_member:
        raise ContributionError('You must be an approved member of this organization to contribute.')
    if not organization.is_active:
        raise ContributionError('This organization is not active.')
    if amount <= 0:
        raise ContributionError('Contribution amount must be greater than zero.')

    set_current_user(user)
    contribution = Contribution.objects.create(
        organization=organization, contributor=user, amount=amount, status=Contribution.IN_PROGRESS
    )
    notify_admins_and_founder(
        organization=organization,
        title='New contribution submitted',
        body=f'{user.email} contributed {amount} in {organization.name}, pending acknowledgement.',
        notification_type=Notification.CONTRIBUTION_SUBMITTED,
        data={'contribution_id': contribution.id},
        exclude_user=user,
    )
    return contribution


def acknowledge_contribution(*, acknowledger, contribution):
    organization = contribution.organization
    acknowledger_membership = Membership.objects.filter(
        organization=organization,
        user=acknowledger,
        role__in=[Membership.FOUNDER, Membership.ADMIN],
        status=Membership.APPROVED,
    ).first()
    if not acknowledger_membership:
        raise ContributionError('Only the Founder or an Admin can acknowledge contributions.')

    is_self_ack = contribution.contributor_id == acknowledger.id
    has_admins = Membership.objects.filter(
        organization=organization, role=Membership.ADMIN, status=Membership.APPROVED
    ).exists()

    if acknowledger_membership.role == Membership.ADMIN and is_self_ack:
        raise ContributionError('You cannot acknowledge your own contribution.')
    # Founders may only self-acknowledge when there are no Admins to do it instead.
    if acknowledger_membership.role == Membership.FOUNDER and is_self_ack and has_admins:
        raise ContributionError('The Founder cannot acknowledge their own contribution while Admins exist.')

    if contribution.status != Contribution.IN_PROGRESS:
        raise ContributionError('This contribution has already been acknowledged.')

    set_current_user(acknowledger)
    with transaction.atomic():
        locked_organization = Organization.objects.select_for_update().get(pk=organization.pk)
        locked_organization.principal_capital += contribution.amount
        locked_organization.save()

        contribution.status = Contribution.ACKNOWLEDGED
        contribution.acknowledged_at = timezone.now()
        contribution.acknowledged_by = acknowledger
        contribution.save()

    notify_user(
        recipient=contribution.contributor,
        title='Contribution acknowledged',
        body=f'Your contribution of {contribution.amount} in {organization.name} has been acknowledged.',
        notification_type=Notification.CONTRIBUTION_ACKNOWLEDGED,
        organization=organization,
        data={'contribution_id': contribution.id},
    )
    return contribution
