from decimal import Decimal

from rest_framework import serializers

from .models import Contribution


class ContributionCreateSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=14, decimal_places=2, min_value=Decimal('0.01'))


class ContributionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contribution
        fields = [
            'id', 'organization', 'contributor', 'amount', 'status',
            'acknowledged_at', 'acknowledged_by', 'created_at',
        ]
        read_only_fields = fields
