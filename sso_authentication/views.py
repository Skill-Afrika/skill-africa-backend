import random
import json
import uuid
from google_auth_oauthlib.flow import Flow
from django.urls import reverse
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import HttpResponseRedirect
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.exceptions import ObjectDoesNotExist
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse

from profile_management.models import User
from freelancer_management.models import FreelancerProfile
from freelancer_management.serializers import FreelanceSerializer
from sponsor_management.models import SponsorProfile
from sponsor_management.serializers import SponsorSerializer
from admin_management.models import AdminProfile
from admin_management.serializers import AdminSerializer

import os
from dotenv import load_dotenv

# Load .env values
load_dotenv()

GOOGLE_SCOPES = [
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
]

PROFILES = {
    "admin": AdminProfile,
    "sponsor": SponsorProfile,
    "freelancer": FreelancerProfile,
}

PROFILE_SERIALIZERS = {
    "admin": AdminSerializer,
    "sponsor": SponsorSerializer,
    "freelancer": FreelanceSerializer,
}


class GoogleStartSignInView(APIView):

    @extend_schema(
        operation_id="google_start_sign_in",
        parameters=[
            OpenApiParameter(
                name="role",
                description="The role of the user. Accepted values are freelancer, sponsor, and admin.",
                required=True,
                type=str,
                enum=["freelancer", "sponsor", "admin"],
            )
        ],
        responses={
            302: OpenApiResponse(
                description="Redirects the user to Google's OAuth 2.0 server for authorization."
            ),
            404: OpenApiResponse(
                description="Path not found",
                response={"error": {"message": "Path not found"}},
            ),
        },
    )
    def get(self, request, role):
        if role not in ["freelancer", "sponsor", "admin"]:
            return Response(
                data={"error": {"message": "Path not found"}},
                status=status.HTTP_404_NOT_FOUND,
            )

        request_state = str(uuid.uuid4())
        client_secret = os.getenv("GOOGLE_CLIENT_SECRET_JSON")
        flow = Flow.from_client_config(
            json.loads(client_secret),
            scopes=GOOGLE_SCOPES,
            state=request_state,
        )
        flow.redirect_uri = os.getenv("SITE_URL") + reverse("google_signin_callback")

        # Generate URL for request to Google's OAuth 2.0 server.
        authorization_url, state = flow.authorization_url(
            access_type="offline", include_granted_scopes="true", prompt="consent"
        )

        if not request.session.session_key:
            request.session.create()
        request.session["google_state"] = state
        request.session["role"] = role
        request.session.save()

        return HttpResponseRedirect(authorization_url)


class GoogleEndSignInView(APIView):

    @extend_schema(
        operation_id="google_end_sign_in",
        parameters=[
            OpenApiParameter(
                name="code",
                description="Authorization code returned by Google's OAuth 2.0 server.",
                required=True,
                type=str,
                location=OpenApiParameter.QUERY,
            ),
            OpenApiParameter(
                name="state",
                description="State parameter returned by Google's OAuth 2.0 server.",
                required=True,
                type=str,
                location=OpenApiParameter.QUERY,
            ),
        ],
        responses={
            201: OpenApiResponse(
                description="User successfully authenticated and tokens generated.",
                response={
                    "user": {
                        "email": "user@example.com",
                        "username": "user1234",
                        "role": "freelancer",
                        "uuid": "user-uuid",
                    },
                    "refresh": "refresh-token",
                    "access": "access-token",
                },
            ),
            502: OpenApiResponse(
                description="Authorization Code not received from SSO or Access token not received from SSO.",
                response={
                    "error": {"message": "Authorization Code not received from SSO."}
                },
            ),
            428: OpenApiResponse(
                description="State Mismatch or Time expired.",
                response={"error": {"message": "State Mismatch. Time expired?"}},
            ),
            405: OpenApiResponse(
                description="Wrong provider used for sign-up.",
                response={"message": "Wrong provider. User signed up with <provider>"},
            ),
            500: OpenApiResponse(
                description="Something went wrong or server error.",
                response={"error": {"message": "Something went wrong"}},
            ),
        },
    )
    def get(self, request):
        code = request.GET.get("code")
        state = request.GET.get("state")
        request_state = request.session["google_state"]
        role = request.session["role"]

        client_secret = os.getenv("GOOGLE_CLIENT_SECRET_JSON")
        flow = Flow.from_client_config(
            json.loads(client_secret),
            scopes=GOOGLE_SCOPES,
            state=request_state,
        )

        if not role:
            return Response(
                {"error": {"message": "Something went wrong"}},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        # First, check for authorization code
        if not code:
            return Response(
                data={
                    "error": {"message": "Authorization Code not received from SSO."}
                },
                status=status.HTTP_502_BAD_GATEWAY,
            )

        if not request_state or state != request_state:
            return Response(
                data={"error": {"message": "State Mismatch. Time expired?"}},
                status=status.HTTP_428_PRECONDITION_REQUIRED,
            )

        # Get Access Token from Google
        try:
            os.environ["OAUTHLIB_RELAX_TOKEN_SCOPE"] = (
                "1"  # This is to fix an error with the scopes being granted.
            )
            flow.redirect_uri = os.getenv("SITE_URL") + reverse(
                "google_signin_callback"
            )
            flow.fetch_token(code=code)
        except Exception as error:
            return Response(
                data={"error": {"message": "Access token not received from SSO."}},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        # Get user data
        session = flow.authorized_session()
        user_info = session.get("https://www.googleapis.com/oauth2/v2/userinfo").json()

        # Check if user exists if not create new user, GoogleSSO model and profile.
        try:
            user = User.objects.get(email=user_info["email"])

            # Check that the user is using the proper signup method
            profile = PROFILES[user.role].objects.get(user__email=user.email)
            provider = profile.provider
            if not provider == "google":
                return Response(
                    data={"message": f"Wrong provider. User signed up with {provider}"},
                    status=status.HTTP_405_METHOD_NOT_ALLOWED,
                )
        except ObjectDoesNotExist:
            # Create a new user
            user = User.objects.create(
                username=user_info["email"].split("@")[0]
                + str(random.randint(1000, 9999)),
                email=user_info["email"],
                password=user_info["picture"] + str(random.randint(10000000, 99999999)),
                role=role,
            )
            user.save()

            try:
                # Then create a profile for the user
                serializer = PROFILE_SERIALIZERS[role](
                    data={
                        "provider": "google",
                        "provider_id": user_info["id"],
                    }
                )
                serializer.is_valid(raise_exception=True)
                serializer.create(
                    validated_data={
                        "user": user,
                        "provider": "google",
                        "provider_id": user_info["id"],
                    }
                )
            except Exception as error:
                print(error)
                return Response(
                    {"error": {"message": "something went wrong"}},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

        # Generate tokens
        refresh = RefreshToken.for_user(user)
        data = {
            "user": {
                "email": user.email,
                "username": user.username,
                "role": user.role,
                "uuid": user.uuid,
            },
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }
        return Response(data, status=status.HTTP_201_CREATED)
