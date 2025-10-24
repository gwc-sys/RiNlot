import jwt
from django.conf import settings
from rest_framework import authentication, exceptions
from django.contrib.auth import get_user_model

User = get_user_model()

class CustomJWTAuthentication(authentication.BaseAuthentication):
    """
    Simple JWT auth that decodes tokens produced by your generate_jwt_token()
    (which encodes payload using settings.SECRET_KEY and HS256).
    Expects Authorization: Bearer <token>
    """
    def authenticate(self, request):
        auth = authentication.get_authorization_header(request).split()
        if not auth or auth[0].lower() != b'bearer':
            return None  # No auth header -> let other authenticators run / or unauthenticated

        if len(auth) == 1:
            raise exceptions.AuthenticationFailed('Invalid Authorization header. No credentials provided.')
        if len(auth) > 2:
            raise exceptions.AuthenticationFailed('Invalid Authorization header. Token string should not contain spaces.')

        token = auth[1]
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed('Token has expired')
        except jwt.InvalidTokenError:
            raise exceptions.AuthenticationFailed('Invalid token')

        user_id = payload.get('user_id')
        if not user_id:
            raise exceptions.AuthenticationFailed('Invalid token payload')

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise exceptions.AuthenticationFailed('User not found')

        return (user, None)