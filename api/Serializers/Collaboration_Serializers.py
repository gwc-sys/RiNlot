from rest_framework import serializers
from django.contrib.auth import get_user_model
from ..model.collaboration_models import *

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 'avatar', 
            'skills', 'role', 'github_username', 'rating', 'availability',
            'college', 'year', 'major', 'date_joined'
        ]
        read_only_fields = ['id', 'date_joined']

class ProjectSerializer(serializers.ModelSerializer):
    owner_name = serializers.CharField(source='owner.get_full_name', read_only=True)
    member_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Project
        fields = [
            'id', 'title', 'description', 'tech_stack', 'skills_needed',
            'owner', 'owner_name', 'members', 'is_public', 'github_repo',
            'demo_url', 'club', 'member_count', 'created_at', 'updated_at'
        ]
    
    def get_member_count(self, obj):
        return obj.members.count()

class MentorSessionSerializer(serializers.ModelSerializer):
    mentor_name = serializers.CharField(source='mentor.get_full_name', read_only=True)
    mentee_name = serializers.CharField(source='mentee.get_full_name', read_only=True)
    
    class Meta:
        model = MentorSession
        fields = [
            'id', 'mentor', 'mentor_name', 'mentee', 'mentee_name', 'date',
            'duration', 'notes', 'rating', 'created_at', 'updated_at'
        ]

class CommunitySerializer(serializers.ModelSerializer):
    member_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Community
        fields = [
            'id', 'name', 'description', 'members', 'is_public', 'topics',
            'member_count', 'created_at', 'updated_at'
        ]
    
    def get_member_count(self, obj):
        return obj.members.count()

class ClubMemberSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    user_avatar = serializers.CharField(source='user.avatar', read_only=True)
    
    class Meta:
        model = ClubMember
        fields = ['id', 'club', 'user', 'user_name', 'user_avatar', 'role', 'joined_at']

class ClubSerializer(serializers.ModelSerializer):
    admin_name = serializers.CharField(source='admin.get_full_name', read_only=True)
    member_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Club
        fields = [
            'id', 'name', 'description', 'category', 'admin', 'admin_name',
            'is_public', 'tags', 'college', 'mission_statement', 'core_focus',
            'faculty_advisor', 'social_links', 'member_count', 'created_at', 'updated_at'
        ]
    
    def get_member_count(self, obj):
        return obj.members.count()

class ClubEventSerializer(serializers.ModelSerializer):
    organizer_name = serializers.CharField(source='organizer.get_full_name', read_only=True)
    attendee_count = serializers.SerializerMethodField()
    registered_count = serializers.SerializerMethodField()
    
    class Meta:
        model = ClubEvent
        fields = [
            'id', 'club', 'title', 'description', 'type', 'date', 'location',
            'organizer', 'organizer_name', 'attendees', 'registered_attendees',
            'max_attendees', 'attendee_count', 'registered_count', 'created_at', 'updated_at'
        ]
    
    def get_attendee_count(self, obj):
        return obj.attendees.count()
    
    def get_registered_count(self, obj):
        return obj.registered_attendees.count()

class ClubPostSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.get_full_name', read_only=True)
    like_count = serializers.SerializerMethodField()
    
    class Meta:
        model = ClubPost
        fields = [
            'id', 'club', 'title', 'content', 'author', 'author_name', 'tags',
            'likes', 'like_count', 'created_at', 'updated_at'
        ]
    
    def get_like_count(self, obj):
        return obj.likes.count()

class ClubResourcesSerializer(serializers.ModelSerializer):
    uploader_name = serializers.CharField(source='uploaded_by.get_full_name', read_only=True)
    
    class Meta:
        model = ClubResources
        fields = [
            'id', 'club', 'name', 'type', 'url', 'uploaded_by', 'uploader_name',
            'downloads', 'created_at', 'updated_at'
        ]

class ProjectGroupSerializer(serializers.ModelSerializer):
    project_title = serializers.CharField(source='project.title', read_only=True)
    member_count = serializers.SerializerMethodField()
    
    class Meta:
        model = ProjectGroup
        fields = [
            'id', 'name', 'description', 'project', 'project_title', 'members',
            'skills', 'looking_for', 'max_members', 'member_count', 'is_active',
            'created_at', 'updated_at'
        ]
    
    def get_member_count(self, obj):
        return obj.members.count()