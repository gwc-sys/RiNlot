from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .Views.dsa_problem_views import (
    ProgressView,
    ProblemListView,
    ProblemDetailView,
    AdminProblemView,
    CommunityProblemView,
    AIGenerateView,
    RunView,
    SubmitView,
)

from .Views.resourceviews import (
    ResourceListCreateView,
    FileUploadView,
    DocumentDetailView,
    DocumentListView,
    DocumentRetrieveUpdateDestroyView,
    DocumentDeleteView,
    DocumentSearchView,
)

# Updated authentication views
from .Views.UserSignUpView import (
    RegisterView, 
    LoginView, 
    LogoutView, 
    me_view,
    FirebaseAuthView,
    ProfileView,
    ChangePasswordView,
    VerifyTokenView,
    RefreshTokenView,
    PublicProfileView
)

# from .Views.UserProfileView import UserProfileView, ProfilePictureUploadView
from .Views.FrontendAppView import FrontendAppView

from .Views.Collaboration_views import (
    UserViewSet,
    ProjectViewSet,
    MentorSessionViewSet,
    CommunityViewSet,
    ClubViewSet,
    ClubEventViewSet,
    ClubPostViewSet,
    ClubResourcesViewSet,
    ProjectGroupViewSet,
)

# Optional: Keep router for backward compatibility if needed
router = DefaultRouter()
router.register(r'projects', ProjectViewSet)
router.register(r'mentorship/sessions', MentorSessionViewSet, basename='mentorship-sessions')
router.register(r'communities', CommunityViewSet)
router.register(r'clubs', ClubViewSet)
router.register(r'events', ClubEventViewSet, basename='events')
router.register(r'posts', ClubPostViewSet, basename='posts')
router.register(r'resources', ClubResourcesViewSet, basename='resources')
router.register(r'project-groups', ProjectGroupViewSet, basename='project-groups')

# ===== Manual path() endpoints for all ViewSets =====

# --- UserViewSet ---
user_list = UserViewSet.as_view({'get': 'list', 'post': 'create'})
user_detail = UserViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'})
user_me = UserViewSet.as_view({'get': 'me'})
user_mentors = UserViewSet.as_view({'get': 'mentors'})
user_become_mentor = UserViewSet.as_view({'post': 'become_mentor'})

# --- ProjectViewSet ---
project_list = ProjectViewSet.as_view({'get': 'list', 'post': 'create'})
project_detail = ProjectViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'})
project_join = ProjectViewSet.as_view({'post': 'join'})

# --- MentorSessionViewSet ---
mentor_session_list = MentorSessionViewSet.as_view({'get': 'list', 'post': 'create'})
mentor_session_detail = MentorSessionViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'})

# --- CommunityViewSet ---
community_list = CommunityViewSet.as_view({'get': 'list', 'post': 'create'})
community_detail = CommunityViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'})

# --- ClubViewSet ---
club_list = ClubViewSet.as_view({'get': 'list', 'post': 'create'})
club_detail = ClubViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'})
club_detail_view = ClubViewSet.as_view({'get': 'detail_view'})
club_join = ClubViewSet.as_view({'post': 'join'})

# --- ClubEventViewSet ---
club_event_list = ClubEventViewSet.as_view({'get': 'list', 'post': 'create'})
club_event_detail = ClubEventViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'})
club_event_register = ClubEventViewSet.as_view({'post': 'register'})

# --- ClubPostViewSet ---
club_post_list = ClubPostViewSet.as_view({'get': 'list', 'post': 'create'})
club_post_detail = ClubPostViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'})
club_post_like = ClubPostViewSet.as_view({'post': 'like'})
club_post_unlike = ClubPostViewSet.as_view({'post': 'unlike'})

# --- ClubResourcesViewSet ---
club_resource_list = ClubResourcesViewSet.as_view({'get': 'list', 'post': 'create'})
club_resource_detail = ClubResourcesViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'})
club_resource_download = ClubResourcesViewSet.as_view({'post': 'download'})

# --- ProjectGroupViewSet ---
project_group_list = ProjectGroupViewSet.as_view({'get': 'list', 'post': 'create'})
project_group_detail = ProjectGroupViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'})
project_group_join = ProjectGroupViewSet.as_view({'post': 'join'})

# ===== URL Patterns =====
urlpatterns = [
    # DRF router endpoints
    path('', include(router.urls)),

    # ===== JWT Authentication Endpoints =====
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('auth/firebase-auth/', FirebaseAuthView.as_view(), name='firebase-auth'),
    path('verify-token/', VerifyTokenView.as_view(), name='verify-token'),
    path('refresh-token/', RefreshTokenView.as_view(), name='refresh-token'),
    
    # User profile endpoints (JWT compatible)
    path('profile/', ProfileView.as_view(), name='profile'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('auth/me/', me_view, name='current-user'),
    
    # Public user profiles
    path('users/public/<str:username>/', PublicProfileView.as_view(), name='public-profile'),

    # ===== Legacy/Additional Profile Endpoints (if needed) =====
    # path('legacy/profile/', UserProfileView.as_view(), name='legacy-user-profile'),
    # path('profile/picture/', ProfilePictureUploadView.as_view(), name='profile-picture'),

    # ===== Resource endpoints =====
    path('resources/', ResourceListCreateView.as_view(), name='resource-list-create'),
    path('upload/', FileUploadView.as_view(), name='file-upload'),
    path('documents/', DocumentListView.as_view(), name='document-list'),
    path('documents/search/', DocumentSearchView.as_view(), name='document-search'),
    path('documents/<pk>/', DocumentDetailView.as_view(), name='document-detail'),
    path('documents/<pk>/edit/', DocumentRetrieveUpdateDestroyView.as_view(), name='document-edit'),
    path('documents/<pk>/delete/', DocumentDeleteView.as_view(), name='document-delete'),

    # ===== DSA problem endpoints =====
    path('problems/', ProblemListView.as_view(), name='problem-list'),
    path('problems/<uuid:problem_id>/', ProblemDetailView.as_view(), name='problem-detail'),
    path('admin/problems/', AdminProblemView.as_view(), name='admin-problems'),
    path('community/problems/', CommunityProblemView.as_view(), name='community-problems'),
    path('ai/generate/', AIGenerateView.as_view(), name='ai-generate'),
    path('run/', RunView.as_view(), name='run'),
    path('submit/', SubmitView.as_view(), name='submit'),
    path('progress/', ProgressView.as_view(), name='progress'),

    # ===== Collaboration endpoints (manual path) =====

    # Users
    path('users/', user_list, name='user-list'),
    path('users/<int:pk>/', user_detail, name='user-detail'),
    path('users/me/', user_me, name='user-me'),
    path('users/mentors/', user_mentors, name='user-mentors'),
    path('users/become-mentor/', user_become_mentor, name='user-become-mentor'),

    # Projects
    path('projects/', project_list, name='project-list-manual'),
    path('projects/<int:pk>/', project_detail, name='project-detail-manual'),
    path('projects/<int:pk>/join/', project_join, name='project-join'),

    # Mentor sessions
    path('mentor-sessions/', mentor_session_list, name='mentor-session-list'),
    path('mentor-sessions/<int:pk>/', mentor_session_detail, name='mentor-session-detail'),

    # Communities
    path('communities/', community_list, name='community-list'),
    path('communities/<int:pk>/', community_detail, name='community-detail'),

    # Clubs
    path('clubs/', club_list, name='club-list'),
    path('clubs/<int:pk>/', club_detail, name='club-detail'),
    path('clubs/<int:pk>/detail_view/', club_detail_view, name='club-detail-view'),
    path('clubs/<int:pk>/join/', club_join, name='club-join'),

    # Club Events
    path('club-events/', club_event_list, name='club-event-list'),
    path('club-events/<int:pk>/', club_event_detail, name='club-event-detail'),
    path('club-events/<int:pk>/register/', club_event_register, name='club-event-register'),

    # Club Posts
    path('club-posts/', club_post_list, name='club-post-list'),
    path('club-posts/<int:pk>/', club_post_detail, name='club-post-detail'),
    path('club-posts/<int:pk>/like/', club_post_like, name='club-post-like'),
    path('club-posts/<int:pk>/unlike/', club_post_unlike, name='club-post-unlike'),

    # Club Resources
    path('club-resources/', club_resource_list, name='club-resource-list'),
    path('club-resources/<int:pk>/', club_resource_detail, name='club-resource-detail'),
    path('club-resources/<int:pk>/download/', club_resource_download, name='club-resource-download'),

    # Project Groups
    path('project-groups/', project_group_list, name='project-group-list'),
    path('project-groups/<int:pk>/', project_group_detail, name='project-group-detail'),
    path('project-groups/<int:pk>/join/', project_group_join, name='project-group-join'),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)