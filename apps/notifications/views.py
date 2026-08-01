from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from apps.base.views import CurrentUserMixin

from . import services
from .models import Notification
from .serializers import DeviceTokenRegisterSerializer, DeviceTokenUnregisterSerializer, NotificationSerializer


class DeviceTokenRegisterView(CurrentUserMixin, generics.GenericAPIView):
    serializer_class = DeviceTokenRegisterSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        services.register_device_token(user=request.user, **serializer.validated_data)
        return Response({'detail': 'Device registered.'}, status=status.HTTP_201_CREATED)


class DeviceTokenUnregisterView(CurrentUserMixin, generics.GenericAPIView):
    serializer_class = DeviceTokenUnregisterSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        services.unregister_device_token(user=request.user, **serializer.validated_data)
        return Response({'detail': 'Device unregistered.'})


class NotificationListView(CurrentUserMixin, generics.ListAPIView):
    serializer_class = NotificationSerializer

    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user)


class NotificationMarkReadView(CurrentUserMixin, generics.GenericAPIView):
    serializer_class = NotificationSerializer

    def post(self, request, notification_id, *args, **kwargs):
        notification = get_object_or_404(Notification, id=notification_id)
        try:
            notification = services.mark_as_read(user=request.user, notification=notification)
        except services.NotificationError as exc:
            raise ValidationError({'detail': str(exc)})
        return Response(NotificationSerializer(notification).data)


class NotificationMarkAllReadView(CurrentUserMixin, generics.GenericAPIView):
    def post(self, request, *args, **kwargs):
        services.mark_all_as_read(user=request.user)
        return Response({'detail': 'All notifications marked as read.'})
