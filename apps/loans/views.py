from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from apps.base.views import CurrentUserMixin
from apps.organizations.models import Organization

from . import services
from .models import Loan
from .serializers import LoanDecisionSerializer, LoanRequestSerializer, LoanSerializer


class LoanRequestCreateView(CurrentUserMixin, generics.GenericAPIView):
    serializer_class = LoanRequestSerializer

    def post(self, request, organization_id, *args, **kwargs):
        organization = get_object_or_404(Organization, id=organization_id)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            loan = services.request_loan(user=request.user, organization=organization, **serializer.validated_data)
        except services.LoanError as exc:
            raise ValidationError({'detail': str(exc)})
        return Response(LoanSerializer(loan).data, status=status.HTTP_201_CREATED)


class LoanDecisionView(CurrentUserMixin, generics.GenericAPIView):
    serializer_class = LoanDecisionSerializer

    def post(self, request, loan_id, *args, **kwargs):
        loan = get_object_or_404(Loan, id=loan_id)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            loan = services.decide_loan(decider=request.user, loan=loan, approve=serializer.validated_data['approve'])
        except services.LoanError as exc:
            raise ValidationError({'detail': str(exc)})
        return Response(LoanSerializer(loan).data)


class LoanSendView(CurrentUserMixin, generics.GenericAPIView):
    serializer_class = LoanSerializer

    def post(self, request, loan_id, *args, **kwargs):
        loan = get_object_or_404(Loan, id=loan_id)
        try:
            loan = services.send_loan(founder=request.user, loan=loan)
        except services.LoanError as exc:
            raise ValidationError({'detail': str(exc)})
        return Response(LoanSerializer(loan).data)


class LoanReceivedView(CurrentUserMixin, generics.GenericAPIView):
    serializer_class = LoanSerializer

    def post(self, request, loan_id, *args, **kwargs):
        loan = get_object_or_404(Loan, id=loan_id)
        try:
            loan = services.mark_loan_received(user=request.user, loan=loan)
        except services.LoanError as exc:
            raise ValidationError({'detail': str(exc)})
        return Response(LoanSerializer(loan).data)


class LoanRepayView(CurrentUserMixin, generics.GenericAPIView):
    serializer_class = LoanSerializer

    def post(self, request, loan_id, *args, **kwargs):
        loan = get_object_or_404(Loan, id=loan_id)
        try:
            loan = services.repay_loan(user=request.user, loan=loan)
        except services.LoanError as exc:
            raise ValidationError({'detail': str(exc)})
        return Response(LoanSerializer(loan).data)
