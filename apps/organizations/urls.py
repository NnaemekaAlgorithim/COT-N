from django.urls import path

from .views import (
    AddCapitalView,
    DemoteToMemberView,
    JoinDecisionView,
    JoinRequestCreateView,
    LeaveOrganizationView,
    OrganizationCreateView,
    OrganizationListView,
    OrganizationMembersListView,
    PromoteToAdminView,
    SubscriptionPaymentVerifyView,
    TransferFounderView,
    paystack_webhook,
)

urlpatterns = [
    path('', OrganizationCreateView.as_view(), name='organization-create'),
    path('search/', OrganizationListView.as_view(), name='organization-list'),
    path('payments/<str:reference>/verify/', SubscriptionPaymentVerifyView.as_view(), name='payment-verify'),
    path('paystack/webhook/', paystack_webhook, name='paystack-webhook'),
    path('<str:organization_id>/join/', JoinRequestCreateView.as_view(), name='join-request-create'),
    path('<str:organization_id>/leave/', LeaveOrganizationView.as_view(), name='organization-leave'),
    path('<str:organization_id>/capital/', AddCapitalView.as_view(), name='organization-add-capital'),
    path('<str:organization_id>/members/', OrganizationMembersListView.as_view(), name='organization-members'),
    path('memberships/<str:membership_id>/decide/', JoinDecisionView.as_view(), name='join-request-decide'),
    path('memberships/<str:membership_id>/promote/', PromoteToAdminView.as_view(), name='membership-promote'),
    path('memberships/<str:membership_id>/demote/', DemoteToMemberView.as_view(), name='membership-demote'),
    path(
        'memberships/<str:membership_id>/transfer-founder/',
        TransferFounderView.as_view(),
        name='membership-transfer-founder',
    ),
]
