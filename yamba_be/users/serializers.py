from rest_framework import serializers
from .models import CustomUser
from django.contrib.auth import authenticate
from django.core.validators import RegexValidator
from django.db import IntegrityError

class CustomUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    username = serializers.CharField(
        max_length=150,
        validators=[
            RegexValidator(
                regex=r'^[a-zA-Z0-9\s]+$',
                message='Username can only contain letters, numbers, and spaces.',
                code='invalid_username'
            ),
        ]
    )

    class Meta:
        model = CustomUser
        fields = [
            'id', 'username', 'email', 'password', 'first_name', 'last_name',
            'phone', 'bio', 'location', 'skills', 'experience_years',
            'linkedin_url', 'github_url', 'portfolio_url', 'profile_picture',
            'is_verified', 'created_at', 'updated_at'
        ]
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def validate_username(self, value):
        # Normalize username by removing extra whitespace
        normalized_username = ' '.join(value.split())
        
        # Check if username already exists
        if CustomUser.objects.filter(username__iexact=normalized_username).exists():
            raise serializers.ValidationError('This username is already taken.')
            
        return normalized_username

    def create(self, validated_data):
        try:
            password = validated_data.pop('password', None)
            user = CustomUser.objects.create(**validated_data)
            if password:
                user.set_password(password)
                user.save()
            return user
        except IntegrityError:
            raise serializers.ValidationError({'username': 'This username is already taken.'})

    def update(self, instance, validated_data):
        try:
            password = validated_data.pop('password', None)
            
            for attr, value in validated_data.items():
                setattr(instance, attr, value)

            if password:
                instance.set_password(password)
                
            instance.save()
            return instance
        except IntegrityError:
            raise serializers.ValidationError({'username': 'This username is already taken.'})

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if not email or not password:
            raise serializers.ValidationError({'non_field_errors': ['Missing email or password']})

        # `authenticate` uses USERNAME_FIELD under the hood, which is 'email' here
        user = authenticate(username=email, password=password)

        if not user:
            raise serializers.ValidationError({'non_field_errors': ['Invalid credentials']})

        if not user.is_active:
            raise serializers.ValidationError({'non_field_errors': ['User account is disabled.']})

        attrs['user'] = user
        return attrs

