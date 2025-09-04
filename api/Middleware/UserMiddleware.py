# app/middleware.py
from django.utils.deprecation import MiddlewareMixin
from ..Middleware import UserMiddleware
from django.utils import timezone  

class SessionCodeMiddleware(MiddlewareMixin):
    def process_request(self, request):
        session_code = request.COOKIES.get("session_code")
        if session_code:
            try:
                session = UserMiddleware.objects.get(code=session_code, is_active=True)
                if session.expires_at < timezone.now():
                    session.is_active = False
                    session.save()
                    request.session_code_valid = False
                else:
                    request.session_code_valid = True
            except UserMiddleware.DoesNotExist:
                request.session_code_valid = False
        else:
            request.session_code_valid = False
