import uuid

from django.db import transaction
from django.utils import timezone

from apps.base.models import set_current_user

from . import paystack
from .models import Membership, Organization, Subscription, SubscriptionPayment

SUBSCRIPTION_PERIOD_DAYS = 30


class OrganizationError(Exception):
    pass


def _generate_reference():
    return f'cotn-{uuid.uuid4().hex}'


def initiate_organization_subscription(*, user, name, description='', is_public=True):
    """Creates a (not-yet-usable) Organization and starts its first Paystack payment."""
    set_current_user(user)
    organization = Organization.objects.create(name=name, description=description, is_public=is_public)
    subscription = Subscription.objects.create(organization=organization, status=Subscription.PENDING)
    return _start_payment(subscription=subscription, user=user, purpose=SubscriptionPayment.INITIAL)


def initiate_subscription_renewal(*, user, organization):
    subscription = organization.subscription
    return _start_payment(subscription=subscription, user=user, purpose=SubscriptionPayment.RENEWAL)


def _start_payment(*, subscription, user, purpose):
    reference = _generate_reference()
    amount_kobo = Subscription.MONTHLY_AMOUNT * 100
    init_data = paystack.initialize_transaction(email=user.email, amount_kobo=amount_kobo, reference=reference)
    payment = SubscriptionPayment.objects.create(
        subscription=subscription,
        paid_by=user,
        reference=reference,
        amount=Subscription.MONTHLY_AMOUNT,
        purpose=purpose,
        status=SubscriptionPayment.PENDING,
        raw_response=init_data,
    )
    return {
        'organization': subscription.organization,
        'reference': payment.reference,
        'authorization_url': init_data['data']['authorization_url'],
    }


def verify_and_activate_payment(*, reference):
    """Idempotent: confirms a Paystack transaction and activates the subscription/org/founder membership."""
    try:
        payment = SubscriptionPayment.objects.select_related('subscription__organization').get(reference=reference)
    except SubscriptionPayment.DoesNotExist:
        raise OrganizationError('No payment found for this reference.')

    if payment.status == SubscriptionPayment.SUCCESS:
        return payment

    verify_data = paystack.verify_transaction(reference=reference)
    transaction_data = verify_data.get('data', {})
    expected_kobo = int(payment.amount * 100)

    if transaction_data.get('status') != 'success' or transaction_data.get('amount') != expected_kobo:
        payment.status = SubscriptionPayment.FAILED
        payment.raw_response = verify_data
        payment.save()
        raise OrganizationError('Payment could not be verified.')

    payment.status = SubscriptionPayment.SUCCESS
    payment.raw_response = verify_data
    payment.save()

    subscription = payment.subscription
    subscription.status = Subscription.ACTIVE
    subscription.current_period_end = timezone.now() + timezone.timedelta(days=SUBSCRIPTION_PERIOD_DAYS)
    subscription.grace_period_ends_at = None
    subscription.save()

    organization = subscription.organization
    organization.is_active = True
    organization.save()

    if payment.purpose == SubscriptionPayment.INITIAL:
        Membership.objects.get_or_create(
            organization=organization,
            user=payment.paid_by,
            defaults={'role': Membership.FOUNDER, 'status': Membership.APPROVED},
        )

    return payment


def request_to_join(*, user, organization):
    if not organization.is_active:
        raise OrganizationError('This organization is not active yet.')
    if Membership.objects.filter(organization=organization, user=user).exists():
        raise OrganizationError('You already have a membership request or membership in this organization.')

    set_current_user(user)
    return Membership.objects.create(
        organization=organization,
        user=user,
        role=Membership.MEMBER,
        status=Membership.PENDING,
    )


def decide_join_request(*, membership, decider, approve):
    decider_membership = Membership.objects.filter(
        organization=membership.organization,
        user=decider,
        role__in=[Membership.FOUNDER, Membership.ADMIN],
        status=Membership.APPROVED,
    ).first()
    if not decider_membership:
        raise OrganizationError('Only the Founder or an Admin can decide on join requests.')
    if membership.status != Membership.PENDING:
        raise OrganizationError('This join request has already been decided.')

    set_current_user(decider)
    membership.status = Membership.APPROVED if approve else Membership.REJECTED
    membership.save()
    return membership


def _get_founder_membership(*, organization, user):
    membership = Membership.objects.filter(
        organization=organization, user=user, role=Membership.FOUNDER, status=Membership.APPROVED
    ).first()
    if not membership:
        raise OrganizationError('Only the Founder can perform this action.')
    return membership


def promote_to_admin(*, founder, membership):
    _get_founder_membership(organization=membership.organization, user=founder)
    if membership.role != Membership.MEMBER or membership.status != Membership.APPROVED:
        raise OrganizationError('Only an approved Member can be promoted to Admin.')

    set_current_user(founder)
    membership.role = Membership.ADMIN
    membership.save()
    return membership


def demote_to_member(*, founder, membership):
    _get_founder_membership(organization=membership.organization, user=founder)
    if membership.role != Membership.ADMIN:
        raise OrganizationError('Only an Admin can be demoted to Member.')

    set_current_user(founder)
    membership.role = Membership.MEMBER
    membership.save()
    return membership


def transfer_founder_role(*, founder, membership):
    founder_membership = _get_founder_membership(organization=membership.organization, user=founder)
    if membership.role != Membership.ADMIN or membership.status != Membership.APPROVED:
        raise OrganizationError('The Founder role can only be transferred to an existing Admin.')

    set_current_user(founder)
    with transaction.atomic():
        # Demote the outgoing Founder first so the unique-founder-per-org constraint never sees two Founders.
        founder_membership.role = Membership.ADMIN
        founder_membership.save()
        membership.role = Membership.FOUNDER
        membership.save()
    return membership


def leave_organization(*, user, organization):
    from apps.loans.models import Loan  # local import: loans app depends on organizations, not the reverse

    membership = Membership.objects.filter(
        organization=organization, user=user, status=Membership.APPROVED
    ).first()
    if not membership:
        raise OrganizationError('You are not an approved member of this organization.')
    if membership.role == Membership.FOUNDER:
        raise OrganizationError('Transfer the Founder role to an Admin before leaving.')
    if Loan.objects.filter(organization=organization, borrower=user, status__in=Loan.UNRESOLVED_STATUSES).exists():
        raise OrganizationError('You cannot leave while you have a pending loan in this organization.')

    membership.delete()


def add_principal_capital(*, founder, organization, amount):
    _get_founder_membership(organization=organization, user=founder)
    if amount <= 0:
        raise OrganizationError('Amount must be greater than zero.')

    set_current_user(founder)
    with transaction.atomic():
        locked_organization = Organization.objects.select_for_update().get(pk=organization.pk)
        locked_organization.principal_capital += amount
        locked_organization.save()
    return locked_organization
