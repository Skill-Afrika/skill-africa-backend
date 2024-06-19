from datetime import datetime, timedelta
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError
from dj_rest_auth.registration.views import RegisterView
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import extend_schema
from .serializers import (
    FreelanceSerializer, 
    SponsorSerializer, 
    AdminSerializer, 
    RegisterSerializer, 
    JWTSerializer, 
    LoginSerializer,
    DocumentationRegisterSerializer
)

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
        request=DocumentationRegisterSerializer,
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
        request=DocumentationRegisterSerializer,
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
        request=DocumentationRegisterSerializer,
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
        self.user = self.serializer.validated_data['user']
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)
        self.refresh_token = str(refresh)

    def get_response(self):
        serializer_class = self.response_serializer
        access_token_expiration = (datetime.now() + timedelta(hours=int(config['ACCESS_TOKEN_LIFETIME_HOURS'])))
        refresh_token_expiration = (datetime.now() + timedelta(days=int(config['REFRESH_TOKEN_LIFETIME_DAYS'])))

        data = {
            'user': self.user,
            'access': self.access_token,
            'refresh': self.refresh_token,
            'access_expiration': access_token_expiration,
            'refresh_expiration': refresh_token_expiration,
        }

        serializer = serializer_class(instance=data)
        response = Response(serializer.data, status=status.HTTP_200_OK)
        return response

    @extend_schema(
        request=LoginSerializer,
        responses={
            201: {
                'type': 'object',
                'properties': {
                    'user': {
                        'type': 'object',
                        'properties': {
                            'username': {'type': 'string'},
                            'email': {'type': 'string'},
                            'role': {'type': 'string'}
                        }
                    },
                    'refresh': {'type': 'string'},
                    'access': {'type': 'string'},
                    'access_expiration': {'type': 'string'},
                    'refresh_expiration': {'type': 'string'},
                },
                 'examples': [
                    {
                        'summary': 'Successful registration',
                        'value': {
                            'user': {'username': 'john_doe', 'email': 'johndoe@example.com', 'role': 'freelancer'},
                            'refresh': 'refresh_token_here',
                            'access': 'access_token_here',
                            "access_expiration": "2024-06-20T16:08:30.615400Z",
                            "refresh_expiration": "2024-06-26T16:08:30.615400Z"
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
        description="Login a User",
        summary="Signs an existing User account in"
    )
    def post(self, request):
        self.request = request
        self.response_serializer = JWTSerializer
        self.serializer = LoginSerializer(data=self.request.data, context={"request": request})
        self.serializer.is_valid(raise_exception=True)

        self.login()
        return self.get_response()



