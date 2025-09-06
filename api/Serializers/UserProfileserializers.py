from rest_framework import serializers
from ..model.UserProfileModel import UserProfiles
from ..model.User import User

class UserProfileSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source="user.id")
    username = serializers.ReadOnlyField(source="user.username")
    email = serializers.ReadOnlyField(source="user.email")
    fullName = serializers.ReadOnlyField(source="user.full_name")
    full_name = serializers.ReadOnlyField(source="user.full_name")  # ✅ Add snake_case version

    # Profile image handling
    profileImage = serializers.SerializerMethodField()
    profile_image = serializers.SerializerMethodField()  # ✅ Add snake_case version

    class Meta:
        model = UserProfiles
        fields = [
            "id", "username", "fullName", "full_name", "email",  # ✅ Include both
            "phone", "bio", "location", "social_links",
            "skills", "interests", "profileImage", "profile_image"  # ✅ Include both
        ]
        extra_kwargs = {
            'phone': {'required': False},
            'bio': {'required': False},
            'location': {'required': False},
            'social_links': {'required': False},
            'skills': {'required': False},
            'interests': {'required': False},
        }

    def get_profileImage(self, obj):
        """Return profile picture URL or initials"""
        if obj.profile_picture:
            return self.context['request'].build_absolute_uri(obj.profile_picture.url)
        return None  # ✅ Return None instead of initials for image field

    def get_profile_image(self, obj):
        """Snake_case version - same logic"""
        return self.get_profileImage(obj)

    def get_initials(self, obj):
        """Separate method for initials (for frontend to use if no image)"""
        full_name = obj.user.get_full_name() or obj.user.username
        return full_name.strip()[0].upper() if full_name else "U"

    def to_representation(self, instance):
        """Add initials to the response"""
        representation = super().to_representation(instance)
        representation['initials'] = self.get_initials(instance)
        return representation