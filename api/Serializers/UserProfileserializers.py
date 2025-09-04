from rest_framework import serializers
from ..model import UserProfiles
from ..model.User import User  # your custom user

class UserProfileSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source="user.id")
    username = serializers.ReadOnlyField(source="user.username")
    email = serializers.ReadOnlyField(source="user.email")
    fullName = serializers.ReadOnlyField(source="user.full_name")

    class Meta:
        model = UserProfiles
        fields = [
            "id", "username", "fullName", "email",
            "phone", "profile_picture", "bio", "location",
            "social_links", "skills", "interests"
        ]

class ProfilePictureSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfiles
        fields = ["profile_picture"]
