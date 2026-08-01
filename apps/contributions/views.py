from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from apps.base.views import CurrentUserMixin
from apps.organizations.models import Organization

from . import services
from .models import Contribution
from .serializers import ContributionCreateSerializer, ContributionSerializer


class ContributionCreateView(CurrentUserMixin, generics.GenericAPIView):
    serializer_class = ContributionCreateSerializer

    def post(self, request, organization_id, *args, **kwargs):
        organization = get_object_or_404(Organization, id=organization_id)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            contribution = services.make_contribution(
                user=request.user, organization=organization, **serializer.validated_data
            )
        except services.ContributionError as exc:
            raise ValidationError({'detail': str(exc)})
        return Response(ContributionSerializer(contribution).data, status=status.HTTP_201_CREATED)


class ContributionAcknowledgeView(CurrentUserMixin, generics.GenericAPIView):
    serializer_class = ContributionSerializer

    def post(self, request, contribution_id, *args, **kwargs):
        contribution = get_object_or_404(Contribution, id=contribution_id)
        try:
            contribution = services.acknowledge_contribution(acknowledger=request.user, contribution=contribution)
        except services.ContributionError as exc:
            raise ValidationError({'detail': str(exc)})
        return Response(ContributionSerializer(contribution).data)
