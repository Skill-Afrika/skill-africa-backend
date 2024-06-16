from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError
from .serializers import FreelanceSerializer, SponsorSerializer, AdminSerializer, RegisterSerializer
from django.conf import settings
from dj_rest_auth.registration.views import RegisterView
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import extend_schema

# Function for registering users
def registerUser(self, request, role):
    serializer = RegisterSerializer(data={**request.data, "role": role})
    serializer.is_valid(raise_exception=True)

    user = RegisterView.perform_create(self, serializer)
    refresh = RefreshToken.for_user(user)
    data = {
        'user': serializer.data,
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }
    return user, data

# Class View for registering Freelancers
class FreelanceRegistrationView(APIView):
    """
    Register a new Freelancers
    """
    @extend_schema(
        request=RegisterSerializer,
        responses={
            201: {
                'type': 'object',
                'properties': {
                    'user': {
                        'type': 'object',
                        'properties': {
                            'username': {'type': 'string'},
                            'email': {'type': 'string'}
                        }
                    },
                    'refresh': {'type': 'string'},
                    'access': {'type': 'string'}
                },
                 'examples': [
                    {
                        'summary': 'Successful registration',
                        'value': {
                            'user': {'username': 'john_doe', 'email': 'johndoe@example.com'},
                            'refresh': 'refresh_token_here',
                            'access': 'access_token_here'
                        }
                    }
                ]
            },
            400: {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string'}
                }
            }
        },
        description="Register a new Freelancer",
        summary="Create a new Freelancer account"
    )
    def post(self, request):
        try:
            user, data = registerUser(self, request, "freelancer") # Register user
            print(user.id)
            serializer = FreelanceSerializer(data={}) # Then create a profile for the user
            serializer.is_valid(raise_exception=True)
            serializer.create(validated_data={'user': user})
        except ValidationError as e:
            return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)

        if data:
            response = Response(
                data,
                status=status.HTTP_201_CREATED
            )
        else:
            response = Response(status=status.HTTP_204_NO_CONTENT)
        return response
    
# Class View for registering Sponsors
class SponsorRegistrationView(APIView):
    """
    Register a new Sponsors
    """
    @extend_schema(
        request=RegisterSerializer,
        responses={
            201: {
                'type': 'object',
                'properties': {
                    'user': {
                        'type': 'object',
                        'properties': {
                            'username': {'type': 'string'},
                            'email': {'type': 'string'}
                        }
                    },
                    'refresh': {'type': 'string'},
                    'access': {'type': 'string'}
                },
                 'examples': [
                    {
                        'summary': 'Successful registration',
                        'value': {
                            'user': {'username': 'john_doe', 'email': 'johndoe@example.com'},
                            'refresh': 'refresh_token_here',
                            'access': 'access_token_here'
                        }
                    }
                ]
            },
            400: {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string'}
                }
            }
        },
        description="Register a new Sponsor",
        summary="Create a new Sponsor account"
    )
    def post(self, request):
        try:
            user, data = registerUser(self, request, "sponsor") # Register user
            serializer = SponsorSerializer(data={}) # Then create a profile for the user
            serializer.is_valid(raise_exception=True)
            serializer.create(validated_data={'user': user})
        except ValidationError as e:
            return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)

        if data:
            response = Response(
                data,
                status=status.HTTP_201_CREATED
            )
        else:
            response = Response(status=status.HTTP_204_NO_CONTENT)
        return response
    
# Class View for registering Admins
class AdminRegistrationView(APIView):
    """
    Register a new Admins
    """
    @extend_schema(
        request=RegisterSerializer,
        responses={
            201: {
                'type': 'object',
                'properties': {
                    'user': {
                        'type': 'object',
                        'properties': {
                            'username': {'type': 'string'},
                            'email': {'type': 'string'}
                        }
                    },
                    'refresh': {'type': 'string'},
                    'access': {'type': 'string'}
                },
                 'examples': [
                    {
                        'summary': 'Successful registration',
                        'value': {
                            'user': {'username': 'john_doe', 'email': 'johndoe@example.com'},
                            'refresh': 'refresh_token_here',
                            'access': 'access_token_here'
                        }
                    }
                ]
            },
            400: {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string'}
                }
            }
        },
        description="Register a new Admin",
        summary="Create a new Admin account"
    )
    def post(self, request):
        try:
            user, data = registerUser(self, request, "admin") # Register user
            serializer = AdminSerializer(data={}) # Then create a profile for the user
            serializer.is_valid(raise_exception=True)
            serializer.create(validated_data={'user': user})
        except ValidationError as e:
            return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)

        if data:
            response = Response(
                data,
                status=status.HTTP_201_CREATED
            )
        else:
            response = Response(status=status.HTTP_204_NO_CONTENT)
        return response
    



    