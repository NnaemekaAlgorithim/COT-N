from decimal import Decimal

from rest_framework import serializers

from .models import Membership, Organization


class OrganizationCreateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=150)
    description = serializers.CharField(required=False, allow_blank=True, default='')
    is_public = serializers.BooleanField(default=True)


class OrganizationSerializer(serializers.ModelSerializer):
    subscription_status = serializers.CharField(source='subscription.status', read_only=True)

    class Meta:
        model = Organization
        fields = [
            'id', 'name', 'description', 'is_public', 'is_active',
            'principal_capital', 'subscription_status', 'created_at',
        ]
        read_only_fields = fields


class SubscriptionPaymentResultSerializer(serializers.Serializer):
    organization = OrganizationSerializer()
    reference = serializers.CharField()
    authorization_url = serializers.CharField()


class MembershipSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = Membership
        fields = ['id', 'organization', 'user', 'email', 'role', 'status', 'created_at']
        read_only_fields = fields


class JoinDecisionSerializer(serializers.Serializer):
    approve = serializers.BooleanField()


class AddCapitalSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=14, decimal_places=2, min_value=Decimal('0.01'))
