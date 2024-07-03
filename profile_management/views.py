from datetime import datetime, timedelta
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from dj_rest_auth.registration.views import RegisterView
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import extend_schema
from .serializers import ( 
    RegisterSerializer, 
    JWTSerializer, 
    LoginSerializer
)
import os

# Get .env values
from dotenv import dotenv_values

from dotenv import load_dotenv

# Load .env values
load_dotenv()

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
        access_token_expiration = (datetime.now() + timedelta(hours=int(os.getenv('ACCESS_TOKEN_LIFETIME_HOURS'))))
        refresh_token_expiration = (datetime.now() + timedelta(days=int(os.getenv('REFRESH_TOKEN_LIFETIME_DAYS'))))

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



