from rest_framework import serializers

from .models import DeviceToken, Notification


class DeviceTokenRegisterSerializer(serializers.Serializer):
    token = serializers.CharField(max_length=255)
    platform = serializers.ChoiceField(choices=DeviceToken.PLATFORM_CHOICES)


class DeviceTokenUnregisterSerializer(serializers.Serializer):
    token = serializers.CharField(max_length=255)


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = [
            'id', 'organization', 'notification_type', 'title', 'body', 'data', 'is_read', 'read_at', 'created_at',
        ]
        read_only_fields = fields
