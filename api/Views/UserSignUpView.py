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
            refresh = RefreshToken.for_user(user)
            return Response({
                'user': serializer.data,
                'refresh': str(refresh),
                'access': str(refresh.access_token),
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
            refresh = RefreshToken.for_user(user)
            session_code = str(uuid.uuid4())
            expiry = timezone.now() + timedelta(hours=2)

            SessionCode.objects.create(user=user, code=session_code, expires_at=expiry)

            response = JsonResponse({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': UserSerializer(user).data,
                'message': 'Login successful'
            })

            # Secure cookie settings
            response.set_cookie(
                key='session_code',
                value=session_code,
                httponly=True,
                secure=False,       # Ensures cookie is sent only over HTTPS
                samesite='Strict',
                max_age=7200       # 2 hours
            )

            return response

        return Response(
            {'error': 'Invalid username/email or password'},
            status=status.HTTP_401_UNAUTHORIZED
        )


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            # Blacklist JWT
            refresh_token = request.data.get("refresh")
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()

            # Invalidate session code
            session_code = request.COOKIES.get("session_code")
            if session_code:
                SessionCode.objects.filter(
                    code=session_code,
                    user=request.user,
                    is_active=True
                ).update(is_active=False)

            # Clear cookie
            response = Response({'message': 'Logout successful'}, status=status.HTTP_200_OK)
            response.delete_cookie("session_code", secure=True)  # Also secure on deletion
            return response

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def me_view(request):
    user = request.user
    # Use getattr to avoid AttributeError if the field doesn't exist
    full_name = getattr(user, 'full_name', None) or getattr(user, 'name', None) or user.username

    return Response({
        'fullName': full_name
    })

