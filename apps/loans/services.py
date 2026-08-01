from django.db import transaction
from django.utils import timezone

from apps.base.models import set_current_user
from apps.notifications.models import Notification
from apps.notifications.services import notify_admins_and_founder, notify_user
from apps.organizations.models import Membership, Organization

from .models import Loan


class LoanError(Exception):
    pass


def _get_approved_membership(*, organization, user):
    return Membership.objects.filter(organization=organization, user=user, status=Membership.APPROVED).first()


def _get_decider_membership(*, organization, user):
    membership = Membership.objects.filter(
        organization=organization, user=user, role__in=[Membership.FOUNDER, Membership.ADMIN], status=Membership.APPROVED
    ).first()
    if not membership:
        raise LoanError('Only the Founder or an Admin can decide on loan requests.')
    return membership


def request_loan(*, user, organization, amount):
    if not _get_approved_membership(organization=organization, user=user):
        raise LoanError('You must be an approved member of this organization to request a loan.')
    if not organization.is_active:
        raise LoanError('This organization is not active.')
    if organization.loan_tenure_days is None or organization.interest_rate_percent is None:
        raise LoanError('The Founder has not configured loan settings for this organization yet.')
    if amount <= 0:
        raise LoanError('Loan amount must be greater than zero.')
    if amount > organization.principal_capital:
        raise LoanError('Requested amount exceeds the available principal capital.')

    set_current_user(user)
    loan = Loan.objects.create(
        organization=organization,
        borrower=user,
        amount=amount,
        status=Loan.PENDING_APPROVAL,
        tenure_days=organization.loan_tenure_days,
        interest_rate_percent=organization.interest_rate_percent,
        defaulter_penalty_rate_percent=organization.defaulter_penalty_rate_percent,
    )
    notify_admins_and_founder(
        organization=organization,
        title='New loan request',
        body=f'{user.email} requested a loan of {amount} in {organization.name}.',
        notification_type=Notification.LOAN_REQUEST_SUBMITTED,
        data={'loan_id': loan.id},
        exclude_user=user,
    )
    return loan


def decide_loan(*, decider, loan, approve):
    _get_decider_membership(organization=loan.organization, user=decider)
    if loan.status != Loan.PENDING_APPROVAL:
        raise LoanError('This loan request has already been decided.')

    set_current_user(decider)
    if approve:
        loan.status = Loan.APPROVED
        loan.approved_at = timezone.now()
    else:
        loan.status = Loan.REJECTED
    loan.save()

    if approve:
        founder_membership = Membership.objects.filter(
            organization=loan.organization, role=Membership.FOUNDER, status=Membership.APPROVED
        ).first()
        if founder_membership:
            notify_user(
                recipient=founder_membership.user,
                title='Loan approved',
                body=f'A loan of {loan.amount} for {loan.borrower.email} in {loan.organization.name} is approved and ready to send.',
                notification_type=Notification.LOAN_APPROVED,
                organization=loan.organization,
                data={'loan_id': loan.id},
            )
    return loan


def send_loan(*, founder, loan):
    membership = Membership.objects.filter(
        organization=loan.organization, user=founder, role=Membership.FOUNDER, status=Membership.APPROVED
    ).first()
    if not membership:
        raise LoanError('Only the Founder can release an approved loan.')
    if loan.status != Loan.APPROVED:
        raise LoanError('Only an approved loan can be sent.')

    set_current_user(founder)
    with transaction.atomic():
        organization = Organization.objects.select_for_update().get(pk=loan.organization_id)
        if loan.amount > organization.principal_capital:
            raise LoanError('Insufficient principal capital to send this loan.')
        organization.principal_capital -= loan.amount
        organization.save()

        loan.status = Loan.SENT
        loan.sent_at = timezone.now()
        loan.save()

    notify_user(
        recipient=loan.borrower,
        title='Loan sent',
        body=f'Your loan of {loan.amount} in {loan.organization.name} has been sent.',
        notification_type=Notification.LOAN_SENT,
        organization=loan.organization,
        data={'loan_id': loan.id},
    )
    return loan


def mark_loan_received(*, user, loan):
    if loan.borrower_id != user.id:
        raise LoanError('Only the borrower can confirm receipt of this loan.')
    if loan.status != Loan.SENT:
        raise LoanError('This loan has not been sent yet.')

    set_current_user(user)
    now = timezone.now()
    loan.status = Loan.RECEIVED
    loan.received_at = now
    loan.due_date = now + timezone.timedelta(days=loan.tenure_days)
    loan.save()
    return loan


def calculate_total_due(loan):
    interest = loan.amount * (loan.interest_rate_percent / 100)
    penalty = 0
    if loan.due_date and timezone.now() > loan.due_date and loan.defaulter_penalty_rate_percent:
        days_overdue = (timezone.now() - loan.due_date).days
        penalty = loan.amount * (loan.defaulter_penalty_rate_percent / 100) * days_overdue
    return loan.amount + interest + penalty


def repay_loan(*, user, loan):
    if loan.borrower_id != user.id:
        raise LoanError('Only the borrower can repay this loan.')
    if loan.status != Loan.RECEIVED:
        raise LoanError('This loan is not awaiting repayment.')

    set_current_user(user)
    total_due = calculate_total_due(loan)
    with transaction.atomic():
        organization = Organization.objects.select_for_update().get(pk=loan.organization_id)
        organization.principal_capital += total_due
        organization.save()

        loan.status = Loan.REPAID
        loan.repaid_at = timezone.now()
        loan.save()

    notify_admins_and_founder(
        organization=loan.organization,
        title='Loan repayment logged',
        body=f'{loan.borrower.email} repaid their loan of {loan.amount} in {loan.organization.name}.',
        notification_type=Notification.LOAN_REPAYMENT_LOGGED,
        data={'loan_id': loan.id},
    )
    return loan
