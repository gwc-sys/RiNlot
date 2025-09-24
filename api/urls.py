# from django.conf import settings
# from django.conf.urls.static import static
# from django.urls import path
# from rest_framework_simplejwt.views import TokenRefreshView
# from .Views.resourceviews import FileUploadView, DocumentDetailView
# from .Views.UserSignUpView import RegisterView, LoginView, LogoutView , me_view  
# from .Views.UserProfileView import UserProfileView, ProfilePictureUploadView

# urlpatterns = [
#     # path('resources/', ResourceListCreateView.as_view()),
#     path('upload/', FileUploadView.as_view()),
#     path('documents/<str:pk>/', DocumentDetailView.as_view()), 
#     path('register/', RegisterView.as_view(), name='register'),  
#     path('login/', LoginView.as_view(), name='login'),          
#     path('logout/', LogoutView.as_view(), name='logout'), 
#     path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),  
#     path('me/', me_view),
#     path("user/profile", UserProfileView.as_view(), name="user-profile"),
#     path("user/profile/picture", ProfilePictureUploadView.as_view(), name="profile-picture"),
# ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)



from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include, re_path
from rest_framework.routers import DefaultRouter

from .Views.dsa_problem_views import ProgressView , ProblemListView, ProblemDetailView, AdminProblemView, CommunityProblemView, AIGenerateView, RunView, SubmitView

from .Views.resourceviews import (
    ResourceListCreateView,
    FileUploadView,
    DocumentDetailView,
    DocumentListView,
    DocumentRetrieveUpdateDestroyView,
    DocumentDeleteView,
    DocumentSearchView
)
from .Views.UserSignUpView import RegisterView, LoginView, LogoutView, me_view  
from .Views.UserProfileView import UserProfileView, ProfilePictureUploadView
from api.Views.FrontendAppView import FrontendAppView

router = DefaultRouter()


urlpatterns = [
    # DRF router endpoints
    path('', include(router.urls)),

    # Authentication endpoints
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('me/', me_view, name='current-user'),
    
    # User profile endpoints
    path('profile/', UserProfileView.as_view(), name='user-profile'),
    path('profile/picture/', ProfilePictureUploadView.as_view(), name='profile-picture'),
    
    # Resource endpoints
    path('resources/', ResourceListCreateView.as_view(), name='resource-list-create'),
    path('upload/', FileUploadView.as_view(), name='file-upload'),
    path('documents/', DocumentListView.as_view(), name='document-list'),
    path('documents/search/', DocumentSearchView.as_view(), name='document-search'),
    path('documents/<pk>/', DocumentDetailView.as_view(), name='document-detail'),
    path('documents/<pk>/edit/', DocumentRetrieveUpdateDestroyView.as_view(), name='document-edit'),
    path('documents/<pk>/delete/', DocumentDeleteView.as_view(), name='document-delete'),

    # DSA problem endpoints
    path('problems/', ProblemListView.as_view(), name='problem-list'),
    path('problems/<uuid:problem_id>/', ProblemDetailView.as_view(), name='problem-detail'),
    path('admin/problems/', AdminProblemView.as_view(), name='admin-problems'),
    path('community/problems/', CommunityProblemView.as_view(), name='community-problems'),
    path('ai/generate/', AIGenerateView.as_view(), name='ai-generate'),
    path('run/', RunView.as_view(), name='run'),
    path('submit/', SubmitView.as_view(), name='submit'),
    path('progress/', ProgressView.as_view(), name='progress'),

    # Frontend app view
    # re_path(r'^.*$', FrontendAppView.as_view(), name='frontend'),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)