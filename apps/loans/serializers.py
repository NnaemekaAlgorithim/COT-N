from decimal import Decimal

from rest_framework import serializers

from .models import Loan


class LoanRequestSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=14, decimal_places=2, min_value=Decimal('0.01'))


class LoanSerializer(serializers.ModelSerializer):
    total_due = serializers.SerializerMethodField()

    class Meta:
        model = Loan
        fields = [
            'id', 'organization', 'borrower', 'amount', 'status',
            'tenure_days', 'interest_rate_percent', 'defaulter_penalty_rate_percent',
            'approved_at', 'sent_at', 'received_at', 'due_date', 'repaid_at', 'total_due', 'created_at',
        ]
        read_only_fields = fields

    def get_total_due(self, obj):
        from .services import calculate_total_due

        if obj.status not in (Loan.RECEIVED, Loan.REPAID):
            return None
        return calculate_total_due(obj)


class LoanDecisionSerializer(serializers.Serializer):
    approve = serializers.BooleanField()
