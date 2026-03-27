from django.contrib.auth import logout
from django.shortcuts import redirect

class AdminLogoutMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith('/admin/'):
            if request.user.is_authenticated and not request.user.is_staff:
                logout(request)
                return redirect('/admin/')
        
        response = self.get_response(request)
        return response