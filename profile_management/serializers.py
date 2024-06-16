from rest_framework import serializers
from .models import FreelancerProfile, SponsorProfile, AdminProfile
from django.contrib.auth import get_user_model
from allauth.account.adapter import get_adapter
from allauth.socialaccount.models import EmailAddress
from allauth.account.utils import setup_user_email
from django.core.exceptions import ValidationError as DjangoValidationError

User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(validated_data['username'], validated_data['email'], validated_data['password'])
        user.role = validated_data['role']
        user.save()
        return user
    
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
        adapter = get_adapter()
        user = adapter.new_user(request)
        self.cleaned_data = self.get_cleaned_data()
        user = adapter.save_user(request, user, self, commit=False)
        if "password" in self.cleaned_data:
            try:
                adapter.clean_password(self.cleaned_data['password'], user=user)
            except DjangoValidationError as exc:
                raise serializers.ValidationError(
                    detail=serializers.as_serializer_error(exc)
                )
        user.save()
        setup_user_email(request, user, [])
        return user

class FreelanceSerializer(serializers.ModelSerializer):
    """
    Serializer for freelancers.
    """
    class Meta:
        model = FreelancerProfile
        fields = '__all__'
        depth = 1


class SponsorSerializer(serializers.ModelSerializer):
    """
    Serializer for sponsors.
    """
    class Meta:
        model = SponsorProfile
        fields = '__all__'
        depth = 1


class AdminSerializer(serializers.ModelSerializer):
    """
    Serializer for admin.
    """
    class Meta:
        model = AdminProfile
        fields = '__all__'
        depth = 1