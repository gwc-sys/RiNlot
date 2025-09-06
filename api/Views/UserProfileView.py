from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from ..model.UserProfileModel import UserProfiles
from ..Serializers.UserProfileserializers import UserProfileSerializer  # Removed ProfilePictureSerializer

# Add the missing serializer here temporarily
from rest_framework import serializers

class ProfilePictureSerializer(serializers.ModelSerializer):
    profileImage = serializers.SerializerMethodField()
    profile_image = serializers.SerializerMethodField()
    initials = serializers.SerializerMethodField()

    class Meta:
        model = UserProfiles
        fields = ["profile_picture", "profileImage", "profile_image", "initials"]
        read_only_fields = ["profileImage", "profile_image", "initials"]

    def get_profileImage(self, obj):
        if obj.profile_picture:
            return self.context['request'].build_absolute_uri(obj.profile_picture.url)
        return None

    def get_profile_image(self, obj):
        return self.get_profileImage(obj)

    def get_initials(self, obj):
        full_name = obj.user.get_full_name() or obj.user.username
        return full_name.strip()[0].upper() if full_name else "U"


class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        profile, created = UserProfiles.objects.get_or_create(user=self.request.user)
        return profile

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class ProfilePictureUploadView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self):
        profile, created = UserProfiles.objects.get_or_create(user=self.request.user)
        return profile

    def post(self, request):
        profile = self.get_object()
        
        if 'profile_picture' not in request.FILES:
            return Response(
                {"error": "No profile picture file provided"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if profile.profile_picture:
            profile.profile_picture.delete()
        
        profile.profile_picture = request.FILES['profile_picture']
        profile.save()
        
        serializer = ProfilePictureSerializer(
            profile, 
            context={'request': request}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request):
        profile = self.get_object()
        
        if profile.profile_picture:
            profile.profile_picture.delete()
            profile.save()
            
            serializer = ProfilePictureSerializer(
                profile,
                context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response(
            {"error": "No profile picture to delete"}, 
            status=status.HTTP_400_BAD_REQUEST
        )