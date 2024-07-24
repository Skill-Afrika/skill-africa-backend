from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError
from drf_spectacular.utils import extend_schema
from .serializers import AdminSerializer
from profile_management.serializers import DocumentationRegisterSerializer
from profile_management.views import registerUser


# Class View for registering Admins
class AdminRegistrationView(APIView):
    """
    Register a new Admins
    """

    @extend_schema(
        request=DocumentationRegisterSerializer,
        responses={
            201: {
                "type": "object",
                "properties": {
                    "user": {
                        "type": "object",
                        "properties": {
                            "username": {"type": "string"},
                            "email": {"type": "string"},
                        },
                    },
                    "refresh": {"type": "string"},
                    "access": {"type": "string"},
                },
                "examples": [
                    {
                        "summary": "Successful registration",
                        "value": {
                            "user": {
                                "username": "john_doe",
                                "email": "johndoe@example.com",
                            },
                            "refresh": "refresh_token_here",
                            "access": "access_token_here",
                        },
                    }
                ],
            },
            400: {"type": "object", "properties": {"error": {"type": "string"}}},
        },
        description="Register a new Admin",
        summary="Create a new Admin account",
    )
    def post(self, request):
        try:
            user, data = registerUser(self, request, "admin")  # Register user
            serializer = AdminSerializer(data={})  # Then create a profile for the user
            serializer.is_valid(raise_exception=True)
            serializer.create(validated_data={"user": user})
        except ValidationError as e:
            error_details = {"error": {}}
            for key in e.detail.keys():
                error_details["error"][key] = e.detail[key][0]

            return Response(data=error_details, status=status.HTTP_400_BAD_REQUEST)

        if data:
            response = Response(data, status=status.HTTP_201_CREATED)
        else:
            response = Response(status=status.HTTP_204_NO_CONTENT)
        return response
