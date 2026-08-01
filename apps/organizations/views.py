import hashlib
import hmac
import json

from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from rest_framework import generics, status
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.response import Response

from apps.base.views import CurrentUserMixin

from . import paystack, services
from .models import Membership, Organization
from .serializers import (
    AddCapitalSerializer,
    JoinDecisionSerializer,
    MembershipSerializer,
    OrganizationCreateSerializer,
    OrganizationSerializer,
    SubscriptionPaymentResultSerializer,
)


class OrganizationCreateView(CurrentUserMixin, generics.GenericAPIView):
    serializer_class = OrganizationCreateSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            result = services.initiate_organization_subscription(user=request.user, **serializer.validated_data)
        except paystack.PaystackError as exc:
            raise ValidationError({'detail': str(exc)})
        return Response(SubscriptionPaymentResultSerializer(result).data, status=status.HTTP_201_CREATED)


class OrganizationListView(generics.ListAPIView):
    serializer_class = OrganizationSerializer

    def get_queryset(self):
        queryset = Organization.objects.filter(is_active=True, is_public=True)
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(name__icontains=search)
        return queryset


class OrganizationMembersListView(CurrentUserMixin, generics.ListAPIView):
    serializer_class = MembershipSerializer

    def get_queryset(self):
        organization = get_object_or_404(Organization, id=self.kwargs['organization_id'])
        is_member = Membership.objects.filter(
            organization=organization, user=self.request.user, status=Membership.APPROVED
        ).exists()
        if not is_member:
            raise PermissionDenied('You must be a member of this organization to view its members.')
        return Membership.objects.filter(organization=organization, status=Membership.APPROVED).select_related('user')


class SubscriptionPaymentVerifyView(generics.GenericAPIView):
    def get(self, request, reference, *args, **kwargs):
        try:
            payment = services.verify_and_activate_payment(reference=reference)
        except services.OrganizationError as exc:
            raise ValidationError({'detail': str(exc)})
        return Response({
            'status': payment.status,
            'organization': OrganizationSerializer(payment.subscription.organization).data,
        })


@csrf_exempt
@require_POST
def paystack_webhook(request):
    signature = request.headers.get('X-Paystack-Signature', '')
    expected = hmac.new(settings.PAYSTACK_SECRET_KEY.encode('utf-8'), request.body, hashlib.sha512).hexdigest()
    if not hmac.compare_digest(signature, expected):
        return HttpResponse(status=401)

    event = json.loads(request.body)
    if event.get('event') == 'charge.success':
        try:
            services.verify_and_activate_payment(reference=event['data']['reference'])
        except services.OrganizationError:
            pass
    return JsonResponse({'received': True})


class JoinRequestCreateView(CurrentUserMixin, generics.GenericAPIView):
    serializer_class = MembershipSerializer

    def post(self, request, organization_id, *args, **kwargs):
        organization = get_object_or_404(Organization, id=organization_id)
        try:
            membership = services.request_to_join(user=request.user, organization=organization)
        except services.OrganizationError as exc:
            raise ValidationError({'detail': str(exc)})
        return Response(MembershipSerializer(membership).data, status=status.HTTP_201_CREATED)


class JoinDecisionView(CurrentUserMixin, generics.GenericAPIView):
    serializer_class = JoinDecisionSerializer

    def post(self, request, membership_id, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        membership = get_object_or_404(Membership, id=membership_id)
        try:
            membership = services.decide_join_request(
                membership=membership, decider=request.user, approve=serializer.validated_data['approve']
            )
        except services.OrganizationError as exc:
            raise ValidationError({'detail': str(exc)})
        return Response(MembershipSerializer(membership).data)


class PromoteToAdminView(CurrentUserMixin, generics.GenericAPIView):
    serializer_class = MembershipSerializer

    def post(self, request, membership_id, *args, **kwargs):
        membership = get_object_or_404(Membership, id=membership_id)
        try:
            membership = services.promote_to_admin(founder=request.user, membership=membership)
        except services.OrganizationError as exc:
            raise ValidationError({'detail': str(exc)})
        return Response(MembershipSerializer(membership).data)


class DemoteToMemberView(CurrentUserMixin, generics.GenericAPIView):
    serializer_class = MembershipSerializer

    def post(self, request, membership_id, *args, **kwargs):
        membership = get_object_or_404(Membership, id=membership_id)
        try:
            membership = services.demote_to_member(founder=request.user, membership=membership)
        except services.OrganizationError as exc:
            raise ValidationError({'detail': str(exc)})
        return Response(MembershipSerializer(membership).data)


class TransferFounderView(CurrentUserMixin, generics.GenericAPIView):
    serializer_class = MembershipSerializer

    def post(self, request, membership_id, *args, **kwargs):
        membership = get_object_or_404(Membership, id=membership_id)
        try:
            membership = services.transfer_founder_role(founder=request.user, membership=membership)
        except services.OrganizationError as exc:
            raise ValidationError({'detail': str(exc)})
        return Response(MembershipSerializer(membership).data)


class LeaveOrganizationView(CurrentUserMixin, generics.GenericAPIView):
    def post(self, request, organization_id, *args, **kwargs):
        organization = get_object_or_404(Organization, id=organization_id)
        try:
            services.leave_organization(user=request.user, organization=organization)
        except services.OrganizationError as exc:
            raise ValidationError({'detail': str(exc)})
        return Response({'detail': 'You have left the organization.'})


class AddCapitalView(CurrentUserMixin, generics.GenericAPIView):
    serializer_class = AddCapitalSerializer

    def post(self, request, organization_id, *args, **kwargs):
        organization = get_object_or_404(Organization, id=organization_id)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            organization = services.add_principal_capital(
                founder=request.user, organization=organization, amount=serializer.validated_data['amount']
            )
        except services.OrganizationError as exc:
            raise ValidationError({'detail': str(exc)})
        return Response(OrganizationSerializer(organization).data)
