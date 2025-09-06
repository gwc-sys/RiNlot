from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate, get_user_model
from ..Serializers.UserSerializer import UserSerializer
from rest_framework.views import APIView
import uuid
from django.utils import timezone
from datetime import timedelta
from django.http import JsonResponse
from ..model.User import SessionCode

User = get_user_model()


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            # ✅ No session code created until login
            return Response({
                'user': serializer.data,
                'message': 'Registration successful. Please login.'
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
            # ✅ Get or create session code (reuses existing active code)
            session_obj, created = SessionCode.objects.get_or_create(
                user=user,
                defaults={'is_active': True}
            )
            
            # ✅ If exists but inactive, reactivate it
            if not created and not session_obj.is_active:
                session_obj.is_active = True
                session_obj.expires_at = timezone.now() + timedelta(days=30)
                session_obj.save()
            # ✅ If exists and active, refresh expiration
            elif not created:
                session_obj.expires_at = timezone.now() + timedelta(days=30)
                session_obj.save()

            response = Response({
                'user': UserSerializer(user).data,
                'session_code': session_obj.code,
                'expires_at': session_obj.expires_at,
                'message': 'Login successful'
            })

            # ✅ Set session code cookie
            response.set_cookie(
                key='session_code',
                value=session_obj.code,
                httponly=True,
                secure=True,       # Change to True in production
                samesite='Strict',
                max_age=2592000      # 30 days
            )

            return response

        return Response(
            {'error': 'Invalid username/email or password'},
            status=status.HTTP_401_UNAUTHORIZED
        )


class LogoutView(APIView):
    def post(self, request):
        try:
            session_code = request.COOKIES.get("session_code") or request.data.get("session_code")
            
            if not session_code:
                return Response(
                    {'error': 'Session code required'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            # ✅ Deactivate session code
            sessions = SessionCode.objects.filter(
                code=session_code,
                is_active=True
            )
            
            if sessions.exists():
                session = sessions.first()
                session.is_active = False
                session.expires_at = timezone.now()  
                session.save()  

            # Clear cookie
            response = Response({'message': 'Logout successful'}, status=status.HTTP_200_OK)
            response.delete_cookie("session_code")
            return response


        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        

@api_view(['GET'])
def me_view(request):
    # Get session code from cookie or header
    session_code = request.COOKIES.get('session_code') or request.headers.get('X-Session-Code')
    
    if not session_code:
        return Response(
            {'error': 'Session code required'}, 
            status=status.HTTP_401_UNAUTHORIZED
        )

    try:
        # ✅ Validate session code
        session = SessionCode.objects.get(code=session_code, is_active=True)
        
        if session.is_expired():
            session.is_active = False
            session.save()
            return Response(
                {'error': 'Session expired'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        user = session.user
        full_name = getattr(user, 'full_name', None) or user.username

        return Response({
            'fullName': full_name,
            'username': user.username,
            'email': user.email,
            'session_expires_at': session.expires_at
        })

    except SessionCode.DoesNotExist:
        return Response(
            {'error': 'Invalid session'}, 
            status=status.HTTP_401_UNAUTHORIZED
        )
