from django.shortcuts import render
import random

from api import serializer as api_serializer
from userauths.models import User, Profile

from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import generics

from rest_framework.permissions import AllowAny, IsAuthenticated
import logging

logger = logging.getLogger(__name__)
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework import status
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.contrib.auth.hashers import check_password

class MyTokenObtainPairView(TokenObtainPairView):
    """
    Login endpoint - obtain JWT access and refresh tokens.

    Takes email and password, returns access and refresh tokens.
    Access token contains user claims (email, username, full_name).

    **Request Body:**
    - email: User's email address
    - password: User's password

    **Response:**
    - access: JWT access token (15 min validity)
    - refresh: JWT refresh token (50 days validity)
    """
    serializer_class = api_serializer.MyTokenObtainPairSerializer


class RegisterView(generics.CreateAPIView):
    """
    User registration endpoint.

    Creates a new user account with email-based authentication.
    Username is auto-generated from email prefix.

    **Request Body:**
    - full_name: User's full name
    - email: Unique email address
    - password: Strong password (validated)
    - password2: Password confirmation

    **Response:**
    - User object with id, email, username, full_name
    """
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = api_serializer.RegisterSerializer
    
def generate_random_otp(length=7):
    otp = ''.join([str(random.randint(0, 9)) for _ in range(length)])
    return otp


class PasswordResetEmailVerifyAPIView(generics.RetrieveAPIView):
    """
    Request password reset via email.

    Generates an OTP and sends a password reset link to the user's email.
    The link contains OTP, user ID, and a temporary refresh token.

    **URL Parameter:**
    - email: User's registered email address

    **Response:**
    - User object if found, or 404 if not found

    **Note:** Even if user not found, response is 200 to prevent user enumeration.
    """
    permission_classes = [AllowAny]
    serializer_class = api_serializer.UserSerializer

    def get_object(self):
        email = self.kwargs['email'] # api/v1/password-email-verify/desphixs@gmail.com/

        user = User.objects.filter(email=email).first()

        if user:
            uuidb64 = user.pk
            refresh = RefreshToken.for_user(user)
            refresh_token = str(refresh.access_token)

            user.refresh_token = refresh_token
            user.otp = generate_random_otp()
            user.save()

            link = f"{settings.FRONTEND_SITE_URL}/create-new-password/?otp={user.otp}&uuidb64={uuidb64}&refresh_token={refresh_token}"

            context = {
                "link": link,
                "username": user.username
            }

            subject = "Password Reset Email"
            text_body = render_to_string("email/password_reset.txt", context)
            html_body = render_to_string("email/password_reset.html", context)

            msg = EmailMultiAlternatives(
                subject=subject,
                from_email=settings.FROM_EMAIL,
                to=[user.email],
                body=text_body
            )

            msg.attach_alternative(html_body, "text/html")
            msg.send()

            logger.info(f"Password reset email sent to {user.email}")
        return user
    
class PasswordChangeAPIView(generics.CreateAPIView):
    """Handle password reset via OTP (from email link)"""
    permission_classes = [AllowAny]
    serializer_class = api_serializer.UserSerializer

    def create(self, request, *args, **kwargs):
        otp = request.data.get('otp')
        uuidb64 = request.data.get('uuidb64')
        password = request.data.get('password')

        if not all([otp, uuidb64, password]):
            return Response({"message": "Missing required fields"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(id=uuidb64, otp=otp)
        except User.DoesNotExist:
            return Response({"message": "Invalid OTP or user"}, status=status.HTTP_404_NOT_FOUND)

        user.set_password(password)
        user.otp = ""  # Clear OTP after successful use
        user.refresh_token = ""  # Clear refresh token after use
        user.save()

        logger.info(f"Password changed successfully for user {user.email}")
        return Response({"message": "Password Changed Successfully"}, status=status.HTTP_201_CREATED)

class ChangePasswordAPIView(generics.CreateAPIView):
    """Handle password change for authenticated users"""
    serializer_class = api_serializer.UserSerializer
    permission_classes = [IsAuthenticated]  # Fixed: Require authentication

    def create(self, request, *args, **kwargs):
        # Fixed: Get user from authenticated token, not from request body (IDOR fix)
        user = request.user
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')

        if not all([old_password, new_password]):
            return Response({"message": "Missing required fields", "icon": "error"}, status=status.HTTP_400_BAD_REQUEST)

        if check_password(old_password, user.password):
            user.set_password(new_password)
            user.save()
            logger.info(f"Password changed for user {user.email}")
            return Response({"message": "Password changed successfully", "icon": "success"})
        else:
            return Response({"message": "Old password is incorrect", "icon": "warning"}, status=status.HTTP_400_BAD_REQUEST)

       