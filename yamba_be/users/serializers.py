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
            'seller_type', 'business_name', 'contact_phone', 'contact_email',
            'address', 'is_paid_seller', 'profile_image'
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
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')
        
        if username and password:
            # Normalize username before authentication
            username = ' '.join(username.split())
            user = authenticate(username=username, password=password)
            if not user:
                raise serializers.ValidationError('Invalid credentials')
        else:
            raise serializers.ValidationError('Missing username or password')
        
        attrs['user'] = user
        return attrs
