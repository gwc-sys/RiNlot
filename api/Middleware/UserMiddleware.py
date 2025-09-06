# middleware.py
from django.http import JsonResponse
from ..model.User import SessionCode

class SessionCodeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Skip for public endpoints
        if request.path in ['/api/login/', '/api/register/']:
            return self.get_response(request)
        
        session_code = request.COOKIES.get('session_code') or request.headers.get('X-Session-Code')
        
        if session_code:
            try:
                session = SessionCode.objects.get(code=session_code, is_active=True)
                
                if not session.is_expired():
                    request.user = session.user  # Attach user to request
                    return self.get_response(request)
                else:
                    session.is_active = False
                    session.save()
                    
            except SessionCode.DoesNotExist:
                pass
        
        return JsonResponse({'error': 'Authentication required'}, status=401)