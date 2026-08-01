from django.contrib.auth import authenticate
from rest_framework import serializers

from .models import User


class RegisterSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError('This email is already in use.')
        return value


class VerifyEmailSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(max_length=6, min_length=6, required=False, allow_blank=True)
    resend = serializers.BooleanField(default=False)

    def validate_email(self, value):
        if not User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError('No user found with this email.')
        return value

    def validate(self, attrs):
        if not attrs.get('resend') and not attrs.get('code'):
            raise serializers.ValidationError({'code': 'This field is required.'})
        return attrs


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        try:
            user = User.objects.get(email__iexact=attrs['email'])
        except User.DoesNotExist:
            raise serializers.ValidationError({'detail': 'Invalid email or password.'})

        if not user.is_active:
            raise serializers.ValidationError({'detail': 'Please verify your email before logging in.'})

        authenticated_user = authenticate(username=user.username, password=attrs['password'])
        if not authenticated_user:
            raise serializers.ValidationError({'detail': 'Invalid email or password.'})

        attrs['user'] = authenticated_user
        return attrs


class PasswordResetRequestSerializer(serializers.Serializer):
    # Deliberately does not validate that the email exists, to avoid account enumeration.
    email = serializers.EmailField()


class PasswordResetConfirmSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(max_length=6, min_length=6)
    new_password = serializers.CharField(write_only=True, min_length=8)

    def validate_email(self, value):
        if not User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError('No user found with this email.')
        return value
