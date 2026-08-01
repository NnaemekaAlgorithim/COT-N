from .models import set_current_user


class CurrentUserMixin:
    """Populates the audit-field ContextVar from the authenticated request user.

    Must precede DRF's generic view classes in the MRO: `initial()` runs
    authentication first, so `request.user` is resolved by the time we read it
    here (unlike plain Django middleware, which runs before DRF authenticates).
    """

    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)
        set_current_user(request.user if request.user.is_authenticated else None)
