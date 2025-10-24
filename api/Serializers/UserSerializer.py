from rest_framework import serializers
from ..model.User import User 
from django.contrib.auth.hashers import make_password

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)
    display_name = serializers.ReadOnlyField()
    
    class Meta:
        model = User
        fields = (
            'id', 
            'username', 
            'email', 
            'password', 
            'full_name', 
            'display_name',
            'firebase_uid',
            'provider',
            'avatar_url',
            'date_joined', 
            'last_login',
            'updated_at',
            'is_active',
            'is_staff',
            'is_superuser',
            'is_verified'
        )
        read_only_fields = (
            'id',
            'date_joined',
            'last_login', 
            'updated_at',
            'is_superuser',
            'is_verified'
        )
    
    def create(self, validated_data):
        # Password is optional for social auth users
        password = validated_data.pop('password', None)
        user = User.objects.create_user(**validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user
    
    def update(self, instance, validated_data):
        if 'password' in validated_data:
            validated_data['password'] = make_password(validated_data['password'])
        return super().update(instance, validated_data)

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)
    confirm_password = serializers.CharField(write_only=True, required=False)
    
    class Meta:
        model = User
        fields = (
            'username',
            'email', 
            'password',
            'confirm_password',
            'full_name',
            'firebase_uid',
            'provider',
            'avatar_url'
        )
        extra_kwargs = {
            'password': {'write_only': True},
            'confirm_password': {'write_only': True},
        }
    
    def validate(self, attrs):
        # For email/password registration, validate password
        if attrs.get('provider') == 'email' and not attrs.get('password'):
            raise serializers.ValidationError({"password": "Password is required for email registration."})
        
        # Check password confirmation if provided
        if attrs.get('password') and attrs.get('confirm_password'):
            if attrs['password'] != attrs['confirm_password']:
                raise serializers.ValidationError({"confirm_password": "Passwords do not match."})
        
        # Remove confirm_password from validated data as it's not a model field
        attrs.pop('confirm_password', None)
        
        return attrs
    
    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = User.objects.create_user(**validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user

class FirebaseAuthSerializer(serializers.Serializer):
    firebase_uid = serializers.CharField(required=True)
    email = serializers.EmailField(required=False, allow_blank=True)
    username = serializers.CharField(required=False, allow_blank=True)
    full_name = serializers.CharField(required=False, allow_blank=True)
    avatar_url = serializers.URLField(required=False, allow_blank=True)
    provider = serializers.CharField(required=False, default='email')
    
    def validate(self, attrs):
        # At least email or username should be provided for social auth
        if not attrs.get('email') and not attrs.get('username'):
            raise serializers.ValidationError(
                "Either email or username must be provided for social authentication."
            )
        return attrs

class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = User.profile.related.related_model  # This references UserProfile
        fields = (
            'id',
            'user',
            'bio',
            'website',
            'location',
            'github_username',
            'twitter_username',
            'linkedin_url',
            'email_notifications',
            'theme_preference',
            'created_at',
            'updated_at'
        )
        read_only_fields = ('id', 'user', 'created_at', 'updated_at')

class PublicUserSerializer(serializers.ModelSerializer):
    """Serializer for public user data (safe to expose)"""
    display_name = serializers.ReadOnlyField()
    
    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'full_name',
            'display_name',
            'avatar_url',
            'date_joined'
        )
        read_only_fields = fields

class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer for user profile updates (excludes sensitive fields)"""
    
    class Meta:
        model = User
        fields = (
            'full_name',
            'avatar_url'
        )

class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True, min_length=6)
    confirm_password = serializers.CharField(required=True, write_only=True)
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "Passwords do not match."})
        return attrs

class SocialLoginSerializer(serializers.Serializer):
    """Serializer for social login requests"""
    provider = serializers.ChoiceField(
        choices=['google', 'github'],
        required=True
    )
    access_token = serializers.CharField(required=True)
    firebase_uid = serializers.CharField(required=True)