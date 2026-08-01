from rest_framework import generics, status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from . import services
from .serializers import LoginSerializer, RegisterSerializer, VerifyEmailSerializer


def _tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {'access': str(refresh.access_token), 'refresh': str(refresh)}


class RegisterView(generics.GenericAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = services.register_user(**serializer.validated_data)
        return Response(
            {'detail': 'Registered successfully. Check your email for a verification code.', 'email': user.email},
            status=status.HTTP_201_CREATED,
        )


class VerifyEmailView(generics.GenericAPIView):
    serializer_class = VerifyEmailSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']

        if serializer.validated_data['resend']:
            services.resend_verification_code(email)
            return Response({'detail': 'A new verification code has been sent to your email.'})

        try:
            user = services.verify_email(email=email, code=serializer.validated_data['code'])
        except services.VerificationError as exc:
            raise ValidationError({'code': str(exc)})

        return Response({'detail': 'Email verified successfully.', **_tokens_for_user(user)})


class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        return Response({'detail': 'Login successful.', **_tokens_for_user(user)})
