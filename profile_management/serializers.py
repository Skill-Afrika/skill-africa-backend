from rest_framework import serializers, exceptions
from .models import User
from django.contrib.auth import get_user_model, authenticate
from allauth.account.adapter import get_adapter
from allauth.socialaccount.models import EmailAddress
from allauth.account.utils import setup_user_email
from django.urls import exceptions as url_exceptions

User = get_user_model()

class DocumentationRegisterSerializer(serializers.ModelSerializer):
    """
    This serializer is purely for documentation puposes
    the original registerSerializer needs the role field to
    function properly but i do not want devs passing in roles
    when using the end point.
    """
    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'role']
        extra_kwargs = {'password': {'write_only': True}}
    
    def validate_username(self, username):
        username = get_adapter().clean_username(username)
        return username

    def validate_email(self, email):
        email = get_adapter().clean_email(email)
        if email and EmailAddress.objects.is_verified(email):
            raise serializers.ValidationError(
                ('A user is already registered with this e-mail address.'),
            )
        return email

    def validate_password(self, password):
        return get_adapter().clean_password(password)

    def get_cleaned_data(self):
        return {
            'username': self.validated_data.get('username', ''),
            'password': self.validated_data.get('password', ''),
            'email': self.validated_data.get('email', ''),
            'role': self.validated_data.get('role', ''),
        }

    def save(self, request):
        self.cleaned_data = self.get_cleaned_data()
        user = User.objects.create(**self.cleaned_data)
        user.role = self.cleaned_data["role"]
        user.set_password(raw_password=self.cleaned_data["password"])

        user.save()
        setup_user_email(request, user, [])
        return user

class UserDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['uuid', 'username', 'email', 'role']

class JWTSerializer(serializers.Serializer):
    """
    Serializer for JWT authentication.
    """
    access = serializers.CharField()
    refresh = serializers.CharField()
    user = serializers.SerializerMethodField()
    access_expiration = serializers.DateTimeField()
    refresh_expiration = serializers.DateTimeField()

    def get_user(self, obj):
        user_data = UserDetailsSerializer(obj['user'], context=self.context).data
        return user_data

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=False)
    email = serializers.CharField(required=False)
    password = serializers.CharField()

    def authenticate(self, email=None, username=None, password=None):
        # make sure the appropriate parameters are passed
        if not email and not username:
            msg = ('Must include either "username" or "email".')
            raise exceptions.ValidationError(msg)
        if not password:
            msg = ('Must include "password".')
            raise exceptions.ValidationError(msg)
        
        # Get user depending on the parameter passed in
        if email:
            user = User.objects.get(email=email)
        elif username:
            user = User.objects.get(username=username)

        # Ensure password is correct
        credentials = {"username": user.username, "password": password}
        check = authenticate(request=self.context["request"], **credentials)
        if not check:
            msg = ('Incorrect Password.')
            raise exceptions.ValidationError(msg)
        return user

    def _validate_username_email(self, username, email, password):
        if email and password:
            user = self.authenticate(email=email, password=password)
        elif username and password:
            user = self.authenticate(username=username, password=password)
        else:
            msg = ('Must include either "username" or "email" and "password".')
            raise exceptions.ValidationError(msg)

        return user

    def get_auth_user_using_allauth(self, username, email, password):
        # Authentication through either username or email
        return self._validate_username_email(username, email, password)

    def get_auth_user(self, username, email, password):
        """
        Retrieve the auth user from given POST payload by using
        `allauth` auth scheme.

        Returns the authenticated user instance if credentials are correct,
        else `None` will be returned
        """
        # When `is_active` of a user is set to False, allauth tries to return template html
        # which does not exist. This is the solution for it. See issue #264.
        try:
            return self.get_auth_user_using_allauth(username, email, password)
        except url_exceptions.NoReverseMatch:
            msg = ('Unable to log in with provided credentials.')
            raise exceptions.ValidationError(msg)

    @staticmethod
    def validate_auth_user_status(user):
        if not user.is_active:
            msg = ('User account is disabled.')
            raise exceptions.ValidationError(msg)

    def validate(self, attrs):
        username = attrs.get('username')
        email = attrs.get('email')
        password = attrs.get('password')
        user = self.get_auth_user(username, email, password)

        if not user:
            msg = ('Unable to log in with provided credentials.')
            raise exceptions.ValidationError(msg)

        # TODO: Check that the user has verified their mail. Later in the project
        # Did we get back an active user?
        self.validate_auth_user_status(user)
        attrs['user'] = user
        return attrs
