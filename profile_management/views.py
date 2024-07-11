from datetime import datetime, timedelta
import os
from django.shortcuts import redirect
from django.urls import reverse
import requests
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from dj_rest_auth.registration.views import RegisterView
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import extend_schema
from dj_rest_auth.registration.views import VerifyEmailView, ResendEmailVerificationView

from profile_management.models import PasswordOTP, User
from .serializers import (
    RegisterSerializer,
    JWTSerializer,
    LoginSerializer,
    PasswordOTPSerializer,
    LogoutSerializer,
    VerifyOTPSerializer,
)
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

# Get .env values
from dotenv import dotenv_values

config = dotenv_values(".env")


# Function for registering users
def registerUser(self, request, role):
    serializer = RegisterSerializer(data={**request.data, "role": role})
    serializer.is_valid(raise_exception=True)

    user = RegisterView.perform_create(self, serializer)
    refresh = RefreshToken.for_user(user)
    data = {
        "user": serializer.data,
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }
    return user, data


class LoginView(APIView):
    """
    Check the credentials and return the REST Token
    if the credentials are valid and authenticated.

    Accept the following POST parameters: username, password
    Return the REST Framework Token Object's key.
    """

    user = None
    access_token = None
    token = None

    def login(self):
        self.user = self.serializer.validated_data["user"]
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)
        self.refresh_token = str(refresh)

    def get_response(self):
        serializer_class = self.response_serializer
        access_token_lifetime_hours = int(os.getenv("ACCESS_TOKEN_LIFETIME_HOURS", 1))  # Default to 1 hour if not set
        refresh_token_lifetime_days = int(os.getenv("REFRESH_TOKEN_LIFETIME_DAYS", 7))  # Default to 7 days if not set

        access_token_expiration = datetime.now() + timedelta(hours=access_token_lifetime_hours)
        refresh_token_expiration = datetime.now() + timedelta(days=refresh_token_lifetime_days)


        data = {
            "user": self.user,
            "access": self.access_token,
            "refresh": self.refresh_token,
            "access_expiration": access_token_expiration,
            "refresh_expiration": refresh_token_expiration,
        }

        serializer = serializer_class(instance=data)
        response = Response(serializer.data, status=status.HTTP_200_OK)
        return response

    @extend_schema(
        request=LoginSerializer,
        responses={
            200: {
                "type": "object",
                "properties": {
                    "user": {
                        "type": "object",
                        "properties": {
                            "username": {"type": "string"},
                            "email": {"type": "string"},
                            "role": {"type": "string"},
                        },
                    },
                    "refresh": {"type": "string"},
                    "access": {"type": "string"},
                    "access_expiration": {"type": "string"},
                    "refresh_expiration": {"type": "string"},
                },
                "examples": [
                    {
                        "summary": "Successful registration",
                        "value": {
                            "user": {
                                "username": "john_doe",
                                "email": "johndoe@example.com",
                                "role": "freelancer",
                            },
                            "refresh": "refresh_token_here",
                            "access": "access_token_here",
                            "access_expiration": "2024-06-20T16:08:30.615400Z",
                            "refresh_expiration": "2024-06-26T16:08:30.615400Z",
                        },
                    }
                ],
            },
            400: {"type": "object", "properties": {"error": {"type": "string"}}},
        },
        description="Login a User",
        summary="Signs an existing User account in",
    )
    def post(self, request):
        self.request = request
        self.response_serializer = JWTSerializer
        self.serializer = LoginSerializer(
            data=self.request.data, context={"request": request}
        )
        self.serializer.is_valid(raise_exception=True)

        self.login()
        return self.get_response()


class LogoutView(APIView):
    """
    Log's user out and deletes the Token object
    assigned to the current User object.

    Accepts/Returns nothing.
    """

    @extend_schema(
        summary="Logout",
        description="Log out the user by deleting their authentication token and blacklisting the refresh token.",
        request=LogoutSerializer,
        responses={
            200: {
                "type": "object",
                "properties": {
                    "detail": {"type": "string"},
                },
                "examples": [
                    {
                        "name": "Success Response",
                        "value": {"detail": "Successfully logged out."},
                    },
                ],
            },
            401: {
                "type": "object",
                "properties": {
                    "detail": {"type": "string"},
                },
                "examples": [
                    {
                        "name": "Error Response (No Refresh Token)",
                        "value": {
                            "detail": "Refresh token was not included in request data."
                        },
                    },
                ],
            },
            500: {
                "type": "object",
                "properties": {
                    "detail": {"type": "string"},
                },
                "examples": [
                    {
                        "name": "Error Response (Invalid/Expired Token)",
                        "value": {"detail": "Token is invalid or expired"},
                    },
                ],
            },
        },
    )
    def post(self, request):
        return self.logout(request)

    def logout(self, request):
        response = Response(
            {"detail": "Successfully logged out."},
            status=status.HTTP_200_OK,
        )

        # add refresh token to blacklist
        try:
            token: RefreshToken = RefreshToken(None)
            try:
                token = RefreshToken(request.data["refresh"])
            except KeyError:
                response.data = {
                    "detail": "Refresh token was not included in request data."
                }
                response.status_code = status.HTTP_401_UNAUTHORIZED

            token.blacklist()
        except (TokenError, AttributeError, TypeError) as error:
            if hasattr(error, "args"):
                if (
                    "Token is blacklisted" in error.args
                    or "Token is invalid or expired" in error.args
                ):
                    response.data = {"detail": error.args[0]}
                    response.status_code = status.HTTP_401_UNAUTHORIZED
                else:
                    response.data = {"detail": "An error has occurred."}
                    response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

            else:
                response.data = {"detail": "An error has occurred."}
                response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return response


class PasswordOTPView(APIView):
    @extend_schema(
        summary="Get OTP for changing password or to login",
        description="Collects users email so that an OTP can be sent to it. To be used to implement changing of password when user forgets it or Login with OTP",
        request=PasswordOTPSerializer,
    )
    def post(self, request):
        # Check that the user has an account
        email = request.data.get("email")
        if not email:
            return Response({"error": "Email is required"}, status=400)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {"error": "User with this email does not exist"}, status=404
            )

        # Delete any existing OTP for the user
        PasswordOTP.objects.filter(email=email).delete()
        serializer = PasswordOTPSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "OTP sent successfully", "data": {"uuid": user.uuid}},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=400)


class VerifyOTPView(APIView):
    user = None

    def login(self, user):
        self.user = user
        refresh = RefreshToken.for_user(user)
        self.access_token = str(refresh.access_token)
        self.refresh_token = str(refresh)

    def get_response(self):
        serializer_class = self.response_serializer
        access_token_lifetime_hours = int(os.getenv("ACCESS_TOKEN_LIFETIME_HOURS", 1))  # Default to 1 hour if not set
        refresh_token_lifetime_days = int(os.getenv("REFRESH_TOKEN_LIFETIME_DAYS", 7))  # Default to 7 days if not set

        access_token_expiration = datetime.now() + timedelta(hours=access_token_lifetime_hours)
        refresh_token_expiration = datetime.now() + timedelta(days=refresh_token_lifetime_days)


        data = {
            "user": self.user,
            "access": self.access_token,
            "refresh": self.refresh_token,
            "access_expiration": access_token_expiration,
            "refresh_expiration": refresh_token_expiration,
        }

        serializer = serializer_class(instance=data)
        response = Response(serializer.data, status=status.HTTP_200_OK)
        return response

    @extend_schema(
        summary="Verify OTP",
        description="Using the OTP sent to the user's email the user can login, then depending on if the flow is for login with code or change password you can then redirect the user to a page where the change password endpoint can be used.",
        request=VerifyOTPSerializer,
        responses={
            200: {
                "type": "object",
                "properties": {
                    "user": {
                        "type": "object",
                        "properties": {
                            "username": {"type": "string"},
                            "email": {"type": "string"},
                            "role": {"type": "string"},
                        },
                    },
                    "refresh": {"type": "string"},
                    "access": {"type": "string"},
                    "access_expiration": {"type": "string"},
                    "refresh_expiration": {"type": "string"},
                },
                "examples": [
                    {
                        "summary": "Successful registration",
                        "value": {
                            "user": {
                                "username": "john_doe",
                                "email": "johndoe@example.com",
                                "role": "freelancer",
                            },
                            "refresh": "refresh_token_here",
                            "access": "access_token_here",
                            "access_expiration": "2024-06-20T16:08:30.615400Z",
                            "refresh_expiration": "2024-06-26T16:08:30.615400Z",
                        },
                    }
                ],
            },
            400: {
                "type": "object",
                "properties": {
                    "error": {"type": "string"},
                },
                "examples": [
                    {
                        "summary": "Invalid Input",
                        "value": {"error": "OTP and UUID are required"},
                    },
                    {
                        "summary": "User Not Found",
                        "value": {"error": "User not found"},
                    },
                    {
                        "summary": "Invalid OTP",
                        "value": {"error": "Invalid OTP"},
                    },
                    {
                        "summary": "OTP Expired",
                        "value": {"error": "OTP has expired"},
                    },
                ],
            },
        },
    )
    def post(self, request, uuid):
        otp = request.data.get("otp")
        if not otp or not uuid:
            return Response(
                {"error": "OTP and UUID are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = User.objects.get(uuid=uuid)
        except User.DoesNotExist:
            return Response(
                {"error": "User not found"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            otp_verification = PasswordOTP.objects.get(email=user.email, code=otp)
        except PasswordOTP.DoesNotExist:
            return Response(
                {"error": "Invalid OTP"}, status=status.HTTP_400_BAD_REQUEST
            )

        now = datetime.now()
        expires_at = otp_verification.expires_at.replace(tzinfo=None)
        if now > expires_at:
            return Response(
                {"error": "OTP has expired"}, status=status.HTTP_400_BAD_REQUEST
            )

        # Log user in and Delete otp after use
        self.login(user)
        otp_verification.delete()
        return self.get_response()


class ConfirmEmail(APIView):
    serializer_class = None

    @extend_schema(
        summary="Confirm Email",
        description="This endpoint confirms the user email by accepting a confirmation key as a path parameter.",
    )
    def get(self, request, verification_code):
        if not verification_code:
            return Response(
                {"error": "Verification Code is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Construct the URL for the second view
        url = request.build_absolute_uri(reverse("verify_email"))

        # Prepare the data to be sent in the POST request
        post_data = {"key": verification_code}

        # Make the POST request to the second view
        response = requests.post(url, data=post_data)

        # Return the response from the second view
        return Response(response.json(), status=response.status_code)


class CustomVerifyEmailView(VerifyEmailView):
    """
    To be used internally
    """


class CustomResendEmailVerificationView(ResendEmailVerificationView):
    """
    Sends a verification link to emails that have not yet been verified.
    Verification is then completed through the confirm email endpoint.
    P.S It does not send the mail to verified emails.
    """
