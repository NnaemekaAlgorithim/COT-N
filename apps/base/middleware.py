from django.utils.deprecation import MiddlewareMixin

from .models import clear_current_user, set_current_user


class CurrentUserMiddleware(MiddlewareMixin):
    def process_request(self, request):
        user = getattr(request, 'user', None)
        if getattr(user, 'is_authenticated', False):
            set_current_user(user)
        else:
            clear_current_user()

    def process_response(self, request, response):
        clear_current_user()
        return response
