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
from django.urls import path
from .Views.resourceviews import FileUploadView, DocumentDetailView
from .Views.UserSignUpView import RegisterView, LoginView, LogoutView, me_view  
from .Views.UserProfileView import UserProfileView, ProfilePictureUploadView

urlpatterns = [
    # Authentication endpoints
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('me/', me_view, name='current-user'),
    
    # User profile endpoints
    path('profile/', UserProfileView.as_view(), name='user-profile'),
    path('profile/picture/', ProfilePictureUploadView.as_view(), name='profile-picture'),
    
    # Resource endpoints
    path('upload/', FileUploadView.as_view(), name='file-upload'),
    path('documents/<pk>/', DocumentDetailView.as_view(), name='document-detail'),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)