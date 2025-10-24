from rest_framework import status, serializers
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
import jwt
from django.conf import settings
from datetime import datetime, timedelta
from django.contrib.auth import get_user_model, authenticate
from ..Serializers.UserSerializer import (
    UserSerializer, 
    UserRegistrationSerializer, 
    FirebaseAuthSerializer,
    PublicUserSerializer,
    UserUpdateSerializer,
    PasswordChangeSerializer,
    SocialLoginSerializer
)
from ..model.User import User
from ..firebase_admin import auth as firebase_auth  # import the firebase_admin.auth
import logging
from django.db import IntegrityError
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

logger = logging.getLogger(__name__)

User = get_user_model()


def generate_jwt_token(user):
    """Generate JWT token for user"""
    payload = {
        'user_id': user.id,
        'username': user.username,
        'email': user.email,
        'exp': datetime.utcnow() + timedelta(days=7),
        'iat': datetime.utcnow()
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
    return token


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            
            # Generate JWT token
            token = generate_jwt_token(user)
            
            return Response({
                'user': UserSerializer(user).data,
                'token': token,
                'message': 'Registration successful'
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(csrf_exempt, name='dispatch')
class FirebaseAuthView(APIView):
    authentication_classes = []          # <<< add this
    permission_classes = [AllowAny]

    def _normalize_provider(self, raw_provider: str) -> str:
        """
        Normalize Firebase providerId like 'google.com' or 'github.com' to the
        model's accepted values ('google', 'github', 'email').
        """
        if not raw_provider:
            return 'email'
        rp = raw_provider.lower()
        # common firebase providerIds include 'google.com', 'github.com', 'facebook.com'
        if 'google' in rp:
            return 'google'
        if 'github' in rp:
            return 'github'
        # default fallback
        return 'email'

    def _extract_id_token(self, request):
        # Accept id_token either in JSON body (id_token) or in Authorization: Bearer <token>
        auth_header = request.META.get('HTTP_AUTHORIZATION') or request.headers.get('Authorization') if hasattr(request, 'headers') else None
        if auth_header:
            parts = auth_header.split()
            if len(parts) == 2 and parts[0].lower() == 'bearer':
                return parts[1]
        # fallback to body
        return request.data.get('id_token') or request.POST.get('id_token')

    def post(self, request):
        serializer = FirebaseAuthSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        firebase_uid = data['firebase_uid']

        # Extract id_token (Authorization header preferred)
        id_token = self._extract_id_token(request)

        # Verify id_token if provided
        if id_token:
            try:
                decoded = firebase_auth.verify_id_token(id_token)
            except Exception as e:
                logger.exception("Firebase token verification failed")
                return Response({'error': 'Invalid Firebase ID token', 'detail': str(e)}, status=status.HTTP_401_UNAUTHORIZED)

            # ensure uid matches
            if decoded.get('uid') != firebase_uid:
                logger.warning("Firebase token uid mismatch: token uid=%s body uid=%s", decoded.get('uid'), firebase_uid)
                return Response({'error': 'Firebase token uid mismatch'}, status=status.HTTP_400_BAD_REQUEST)

        # Normalize provider
        raw_provider = data.get('provider', 'email')
        provider = self._normalize_provider(raw_provider)

        try:
            # 1) Try to find user already linked with this firebase_uid
            user = User.objects.filter(firebase_uid=firebase_uid).first()

            if user:
                # Update any missing info on the existing linked user
                if data.get('email') and user.email != data['email']:
                    user.email = data['email']
                if data.get('full_name') and not user.full_name:
                    user.full_name = data['full_name']
                if data.get('avatar_url') and not user.avatar_url:
                    user.avatar_url = data['avatar_url']
                user.provider = provider
                user.save()
            else:
                # 2) If no firebase_uid match, try to find an account with the same email and link it
                email = data.get('email') or ''
                existing_by_email = User.objects.filter(email__iexact=email).first() if email else None

                if existing_by_email:
                    # Link Firebase UID to the existing email account (defensive)
                    if existing_by_email.firebase_uid and existing_by_email.firebase_uid != firebase_uid:
                        # Conflict: another firebase uid already linked
                        raise IntegrityError(f"Account with email {email} already linked to another firebase uid.")
                    existing_by_email.firebase_uid = firebase_uid
                    existing_by_email.provider = provider
                    if data.get('full_name') and not existing_by_email.full_name:
                        existing_by_email.full_name = data['full_name']
                    if data.get('avatar_url') and not existing_by_email.avatar_url:
                        existing_by_email.avatar_url = data['avatar_url']
                    existing_by_email.is_verified = True
                    existing_by_email.save()
                    user = existing_by_email
                else:
                    # 3) Create a new user (ensure unique username)
                    username = data.get('username') or (email.split('@')[0] if email else None) or f"user_{firebase_uid[:8]}"
                    base_username = username
                    counter = 1
                    while User.objects.filter(username=username).exists():
                        username = f"{base_username}{counter}"
                        counter += 1

                    user_data = {
                        'username': username,
                        'email': email,
                        'full_name': data.get('full_name', ''),
                        'firebase_uid': firebase_uid,
                        'avatar_url': data.get('avatar_url', ''),
                        'provider': provider,
                        'is_verified': True
                    }
                    user = User.objects.create_user(**user_data)

            # Success -> generate JWT and return user
            token = generate_jwt_token(user)
            return Response({
                'message': 'Authentication successful',
                'user': UserSerializer(user).data,
                'token': token
            }, status=status.HTTP_200_OK)

        except IntegrityError as ie:
            logger.exception("IntegrityError while syncing social user")
            return Response({'error': 'Backend sync failed', 'detail': str(ie)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            # Log stacktrace for debugging and return a readable error
            logger.exception("Unexpected error while syncing social user")
            return Response({'error': 'Backend sync failed', 'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        login_identifier = request.data.get('username')
        password = request.data.get('password')

        if not login_identifier or not password:
            return Response(
                {'error': 'Username/email and password are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Try username authentication
        user = authenticate(username=login_identifier, password=password)

        # If not found, try email authentication
        if not user and '@' in login_identifier:
            try:
                user_by_email = User.objects.get(email__iexact=login_identifier)
                user = authenticate(username=user_by_email.username, password=password)
            except User.DoesNotExist:
                user = None

        if user:
            # Generate JWT token
            token = generate_jwt_token(user)
            
            return Response({
                'user': UserSerializer(user).data,
                'token': token,
                'message': 'Login successful'
            })

        return Response(
            {'error': 'Invalid username/email or password'},
            status=status.HTTP_401_UNAUTHORIZED
        )


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # With JWT, logout is handled on client side by removing the token
        # Optional: You could implement token blacklisting here if using JWTToken model
        
        return Response({
            'message': 'Logout successful. Please remove the token on client side.'
        }, status=status.HTTP_200_OK)


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Get current user profile"""
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    def put(self, request):
        """Update user profile"""
        serializer = UserUpdateSerializer(
            request.user, 
            data=request.data, 
            partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response({
                'user': serializer.data,
                'message': 'Profile updated successfully'
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = PasswordChangeSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            
            # Check old password
            if not user.check_password(serializer.validated_data['old_password']):
                return Response(
                    {'error': 'Current password is incorrect'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Set new password
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            
            # Generate new token since password changed
            token = generate_jwt_token(user)
            
            return Response({
                'message': 'Password changed successfully',
                'token': token  # Return new token
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyTokenView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Verify if the current JWT token is valid"""
        serializer = UserSerializer(request.user)
        return Response({
            'valid': True,
            'user': serializer.data
        })


class PublicProfileView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, username):
        """Get public user profile"""
        try:
            user = User.objects.get(username=username, is_active=True)
            serializer = PublicUserSerializer(user)
            return Response(serializer.data)
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def me_view(request):
    """Get current user info (compatible with your existing frontend)"""
    user = request.user
    full_name = getattr(user, 'full_name', None) or user.username

    return Response({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'is_superuser': user.is_superuser,
        'is_staff': user.is_staff,
        'fullName': full_name,
        'avatar_url': user.avatar_url,
        'provider': user.provider
    })


# Optional: Token refresh endpoint
class RefreshTokenView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Refresh JWT token"""
        user = request.user
        token = generate_jwt_token(user)
        
        return Response({
            'token': token,
            'message': 'Token refreshed successfully'
        })


class UserRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'full_name', 'avatar_url', 'provider')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = User.objects.create_user(**validated_data)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save()
        return user