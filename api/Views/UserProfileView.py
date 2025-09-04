from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from ..model.UserProfileModel import UserProfiles
from ..Serializers.UserProfileserializers import UserProfileSerializer, ProfilePictureSerializer

class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user.profile  
        

class ProfilePictureUploadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        profile = request.user.profile
        serializer = ProfilePictureSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"profilePictureUrl": profile.profile_picture.url}, status=200)
        return Response(serializer.errors, status=400)

    def delete(self, request):
        profile = request.user.profile
        if profile.profile_picture:
            profile.profile_picture.delete(save=True)
        return Response({"message": "Profile picture removed successfully"}, status=200)
