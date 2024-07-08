from rest_framework import serializers, exceptions
from .models import User
from django.contrib.auth import get_user_model, authenticate
from allauth.account.adapter import get_adapter
from allauth.socialaccount.models import EmailAddress
from allauth.account.utils import setup_user_email
from django.urls import exceptions as url_exceptions
from dj_rest_auth.serializers import PasswordResetSerializer
from django.contrib.auth.forms import PasswordResetForm

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
        fields = ["username", "email", "password"]
        extra_kwargs = {"password": {"write_only": True}}


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "email", "password", "role"]
        extra_kwargs = {"password": {"write_only": True}}

    def validate_username(self, username):
        username = get_adapter().clean_username(username)
        return username

    def validate_email(self, email):
        email = get_adapter().clean_email(email)
        if email and EmailAddress.objects.is_verified(email):
            raise serializers.ValidationError(
                ("A user is already registered with this e-mail address."),
            )
        return email

    def validate_password(self, password):
        return get_adapter().clean_password(password)

    def get_cleaned_data(self):
        return {
            "username": self.validated_data.get("username", ""),
            "password": self.validated_data.get("password", ""),
            "email": self.validated_data.get("email", ""),
            "role": self.validated_data.get("role", ""),
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
        fields = ["uuid", "username", "email", "role"]


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
        user_data = UserDetailsSerializer(obj["user"], context=self.context).data
        return user_data


class LoginSerializer(serializers.Serializer):
    """
    Serializer for user login that supports authentication using either
    username or email along with a password.
    """

    username = serializers.CharField(required=False)
    email = serializers.CharField(required=False)
    password = serializers.CharField()

    def authenticate(self, email=None, username=None, password=None):
        """
        Authenticates a user using email or username and password.

        Args:
            email (str, optional): The email of the user.
            username (str, optional): The username of the user.
            password (str): The password of the user.

        Raises:
            ValidationError: If neither email nor username is provided,
                             or if the password is not provided,
                             or if the user does not exist,
                             or if the password is incorrect.

        Returns:
            User: The authenticated user instance.
        """
        if not email and not username:
            raise exceptions.ValidationError(
                'Must include either "username" or "email".'
            )
        if not password:
            raise exceptions.ValidationError('Must include "password".')

        try:
            if email:
                user = User.objects.get(email=email)
            elif username:
                user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise exceptions.ValidationError(
                "User with the provided email/username does not exist."
            )

        credentials = {"username": user.username, "password": password}
        authenticated_user = authenticate(
            request=self.context.get("request"), **credentials
        )
        if not authenticated_user:
            raise exceptions.ValidationError("Incorrect password.")
        return authenticated_user

    def _validate_username_email(self, username, email, password):
        """
        Validates the user credentials using either username or email.

        Args:
            username (str, optional): The username of the user.
            email (str, optional): The email of the user.
            password (str): The password of the user.

        Raises:
            ValidationError: If neither username nor email is provided,
                             or if the password is not provided,
                             or if the authentication fails.

        Returns:
            User: The authenticated user instance.
        """
        if email and password:
            user = self.authenticate(email=email, password=password)
        elif username and password:
            user = self.authenticate(username=username, password=password)
        else:
            raise exceptions.ValidationError(
                'Must include either "username" or "email" and "password".'
            )

        return user

    def get_auth_user_using_allauth(self, username, email, password):
        """
        Authenticates the user using either username or email and password
        through the allauth authentication scheme.

        Args:
            username (str, optional): The username of the user.
            email (str, optional): The email of the user.
            password (str): The password of the user.

        Returns:
            User: The authenticated user instance.
        """
        return self._validate_username_email(username, email, password)

    def get_auth_user(self, username, email, password):
        """
        Retrieves the authenticated user using the provided credentials.

        Args:
            username (str, optional): The username of the user.
            email (str, optional): The email of the user.
            password (str): The password of the user.

        Raises:
            ValidationError: If the authentication fails.

        Returns:
            User: The authenticated user instance, or None if authentication fails.
        """
        try:
            return self.get_auth_user_using_allauth(username, email, password)
        except exceptions.ValidationError as e:
            raise e
        except Exception as e:
            raise exceptions.ValidationError(
                "Unable to log in with provided credentials."
            )

    @staticmethod
    def validate_auth_user_status(user):
        """
        Validates the status of the authenticated user.

        Args:
            user (User): The authenticated user instance.

        Raises:
            ValidationError: If the user account is disabled.
        """
        if not user.is_active:
            raise exceptions.ValidationError("User account is disabled.")

    def validate(self, attrs):
        """
        Validates the authentication credentials provided in the request.

        Args:
            attrs (dict): The request data containing username/email and password.

        Raises:
            ValidationError: If the authentication fails.

        Returns:
            dict: The validated data including the authenticated user instance.
        """
        username = attrs.get("username")
        email = attrs.get("email")
        password = attrs.get("password")
        user = self.get_auth_user(username, email, password)

        if not user:
            raise exceptions.ValidationError(
                "Unable to log in with provided credentials."
            )

        # TODO: Check that the user has verified their email. (to be implemented later)

        self.validate_auth_user_status(user)
        attrs["user"] = user
        return attrs


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField(required=True)


class CustomPasswordResetSerializer(PasswordResetSerializer):
    # @property
    # def password_reset_form_class(self):
    #     return PasswordResetForm
    pass
