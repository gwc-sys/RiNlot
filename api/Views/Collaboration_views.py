from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.contrib.auth import get_user_model
from django.db.models import Q
from ..model.collaboration_models import *
from ..Serializers.Collaboration_Serializers import *

User = get_user_model()

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return User.objects.all()
        return User.objects.filter(id=self.request.user.id)
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def mentors(self, request):
        mentors = User.objects.filter(role='mentor', availability=True)
        serializer = self.get_serializer(mentors, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def become_mentor(self, request):
        user = request.user
        user.role = 'mentor'
        user.save()
        serializer = self.get_serializer(user)
        return Response(serializer.data)

class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]

    
    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Project.objects.all()
        return Project.objects.filter(
            Q(is_public=True) | Q(members=user) | Q(owner=user)
        ).distinct()
    
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
    
    @action(detail=True, methods=['post'])
    def join(self, request, pk=None):
        project = self.get_object()
        project.members.add(request.user)
        serializer = self.get_serializer(project)
        return Response(serializer.data)

class MentorSessionViewSet(viewsets.ModelViewSet):
    queryset = MentorSession.objects.all()
    serializer_class = MentorSessionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return MentorSession.objects.all()
        return MentorSession.objects.filter(
            Q(mentor=user) | Q(mentee=user)
        ).distinct()
    
    def perform_create(self, serializer):
        serializer.save()

class CommunityViewSet(viewsets.ModelViewSet):
    queryset = Community.objects.all()
    serializer_class = CommunitySerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Community.objects.all()
        return Community.objects.filter(
            Q(is_public=True) | Q(members=user)
        ).distinct()
    
    def perform_create(self, serializer):
        community = serializer.save()
        community.members.add(self.request.user)

class ClubViewSet(viewsets.ModelViewSet):
    queryset = Club.objects.all()
    serializer_class = ClubSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Club.objects.all()
        return Club.objects.filter(
            Q(is_public=True) | Q(members=user)
        ).distinct()
    
    def perform_create(self, serializer):
        club = serializer.save(admin=self.request.user)
        ClubMember.objects.create(club=club, user=self.request.user, role='president')
    
    @action(detail=True, methods=['get'])
    def detail_view(self, request, pk=None):
        club = self.get_object()
        members = ClubMember.objects.filter(club=club)
        events = ClubEvent.objects.filter(club=club)
        resources = ClubResources.objects.filter(club=club)
        
        data = {
            'club': ClubSerializer(club).data,
            'members': ClubMemberSerializer(members, many=True).data,
            'events': ClubEventSerializer(events, many=True).data,
            'resources': ClubResourcesSerializer(resources, many=True).data,
        }
        return Response(data)
    
    @action(detail=True, methods=['post'])
    def join(self, request, pk=None):
        club = self.get_object()
        if club.is_public:
            ClubMember.objects.get_or_create(club=club, user=request.user, defaults={'role': 'member'})
            serializer = self.get_serializer(club)
            return Response(serializer.data)
        else:
            return Response(
                {'error': 'This club requires approval to join'}, 
                status=status.HTTP_403_FORBIDDEN
            )

class ClubEventViewSet(viewsets.ModelViewSet):
    queryset = ClubEvent.objects.all()
    serializer_class = ClubEventSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return ClubEvent.objects.all()
        return ClubEvent.objects.filter(
            Q(club__is_public=True) | Q(club__members=user)
        ).distinct()
    
    def perform_create(self, serializer):
        serializer.save(organizer=self.request.user)
    
    @action(detail=True, methods=['post'])
    def register(self, request, pk=None):
        event = self.get_object()
        if event.max_attendees and event.registered_attendees.count() >= event.max_attendees:
            return Response(
                {'error': 'Event is full'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        event.registered_attendees.add(request.user)
        serializer = self.get_serializer(event)
        return Response(serializer.data)

class ClubPostViewSet(viewsets.ModelViewSet):
    queryset = ClubPost.objects.all()
    serializer_class = ClubPostSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        club_id = self.request.query_params.get('club_id')
        queryset = ClubPost.objects.all()
        
        if club_id:
            queryset = queryset.filter(club_id=club_id)
        
        if not user.is_staff:
            queryset = queryset.filter(
                Q(club__is_public=True) | Q(club__members=user)
            )
        
        return queryset.distinct()
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
    
    @action(detail=True, methods=['post'])
    def like(self, request, pk=None):
        post = self.get_object()
        post.likes.add(request.user)
        serializer = self.get_serializer(post)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def unlike(self, request, pk=None):
        post = self.get_object()
        post.likes.remove(request.user)
        serializer = self.get_serializer(post)
        return Response(serializer.data)

class ClubResourcesViewSet(viewsets.ModelViewSet):
    queryset = ClubResources.objects.all()
    serializer_class = ClubResourcesSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        club_id = self.request.query_params.get('club_id')
        queryset = ClubResources.objects.all()
        
        if club_id:
            queryset = queryset.filter(club_id=club_id)
        
        if not user.is_staff:
            queryset = queryset.filter(
                Q(club__is_public=True) | Q(club__members=user)
            )
        
        return queryset.distinct()
    
    def perform_create(self, serializer):
        serializer.save(uploaded_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def download(self, request, pk=None):
        resource = self.get_object()
        resource.downloads += 1
        resource.save()
        serializer = self.get_serializer(resource)
        return Response(serializer.data)

class ProjectGroupViewSet(viewsets.ModelViewSet):
    queryset = ProjectGroup.objects.filter(is_active=True)
    serializer_class = ProjectGroupSerializer
    permission_classes = [IsAuthenticated]
    
    def perform_create(self, serializer):
        group = serializer.save()
        group.members.add(self.request.user)
    
    @action(detail=True, methods=['post'])
    def join(self, request, pk=None):
        group = self.get_object()
        if group.members.count() >= group.max_members:
            return Response(
                {'error': 'Group is full'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        group.members.add(request.user)
        serializer = self.get_serializer(group)
        return Response(serializer.data)