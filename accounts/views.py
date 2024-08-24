from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from .serializers import UserSerializer, RegisterSerializer, PasswordResetSerializer, PasswordResetConfirmSerializer, LoginSerializer, EmailVerificationSerializer
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.core.mail import send_mail
from django.conf import settings
import random
from .models import TemporaryUser
from django.utils import timezone
from datetime import timedelta



class RegisterView(generics.GenericAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        # Cleanup old TemporaryUser entries
        TemporaryUser.cleanup_expired()

        # Check if username or email is already in use
        username = request.data.get('username')
        email = request.data.get('email')

        existing_user = TemporaryUser.objects.filter(username=username).first() or \
                        TemporaryUser.objects.filter(email=email).first()

        if existing_user:
            time_since_creation = timezone.now() - existing_user.created_at
            if time_since_creation < timedelta(minutes=5):
                return Response({
                    "detail": "You cannot register with this username or email right now. Please try again after 5 minutes or use different credentials."
                }, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            temp_user = serializer.save()

            # Generate a random verification code
            verification_code = random.randint(100000, 999999)
            temp_user.verification_code = verification_code
            temp_user.save()

            # Send verification email
            send_mail(
                'Email Verification',
                f'Your verification code is {temp_user.verification_code}',
                settings.DEFAULT_FROM_EMAIL,
                [temp_user.email],
                fail_silently=False,
            )

            # Send response with temporary user ID
            response_data = {
                'detail': 'Check your email for the verification code.',
                'temp_user_id': temp_user.id
            }
            return Response(response_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = authenticate(email=serializer.validated_data['email'], password=serializer.validated_data['password'])
            if user:
                login(request, user)
                refresh = RefreshToken.for_user(user)
                return Response({
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                })
            return Response({'detail': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetView(generics.GenericAPIView):
    serializer_class = PasswordResetSerializer
    permission_classes = [AllowAny]
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save(request=request)  # Pass the request object here
            return Response({"detail": "Password reset link has been sent to your email."}, status=200)
        return Response(serializer.errors, status=400)

class PasswordResetConfirmView(generics.GenericAPIView):
    serializer_class = PasswordResetConfirmSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        uidb64 = request.data.get('uidb64')
        token = request.data.get('token')
        new_password = request.data.get('new_password')

        if not uidb64 or not token:
            return Response({"detail": "Missing uidb64 or token in the request data."},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
            if not default_token_generator.check_token(user, token):
                return Response({"detail": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST)

            # If the token is valid, set the new password
            user.set_password(new_password)
            user.save()
            return Response({"detail": "Password has been reset successfully."}, status=status.HTTP_200_OK)

        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response({"detail": "Invalid user."}, status=status.HTTP_400_BAD_REQUEST)



class EmailVerificationView(generics.GenericAPIView):
    serializer_class = EmailVerificationSerializer
    permission_classes = [AllowAny]
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            temp_user_id = request.data.get('temp_user_id')
            try:
                temp_user = TemporaryUser.objects.get(id=temp_user_id)

                if temp_user.verification_code == serializer.validated_data['code']:

                    # Check for email and username uniqueness
                    if User.objects.filter(email=temp_user.email).exists():
                        return Response({'detail': 'This email is already registered.'},
                                        status=status.HTTP_400_BAD_REQUEST)
                    if User.objects.filter(username=temp_user.username).exists():
                        return Response({'detail': 'This username is already taken.'},
                                        status=status.HTTP_400_BAD_REQUEST)

                    user = get_user_model().objects.create_user(
                        username=temp_user.username,
                        email=temp_user.email,
                        password=temp_user.password
                    )
                    user.is_active = True
                    user.save()

                    # Specify the backend to use for login
                    backend = 'accounts.backends.EmailBackend'  # Replace 'yourapp' with the actual app name where EmailBackend is located
                    user.backend = backend

                    login(request, user, backend=backend)
                    temp_user.delete()

                    refresh = RefreshToken.for_user(user)
                    return Response({
                        'refresh': str(refresh),
                        'access': str(refresh.access_token),
                    })
                else:
                    return Response({'detail': 'Invalid verification code.'}, status=status.HTTP_400_BAD_REQUEST)
            except TemporaryUser.DoesNotExist:
                return Response({'detail': 'Temporary user not found.'}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class HomeView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        content = {'message': 'Hello, World!'}
        return Response(content)
