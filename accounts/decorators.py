from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect


def role_required(*allowed_roles):
    """
    Usage:
        @role_required('SUPER_ADMIN')
        def some_view(request): ...
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped(request, *args, **kwargs):
            if request.user.role not in allowed_roles:
                messages.error(request, "You do not have permission to access that page.")
                return redirect('accounts:dashboard_redirect')
            return view_func(request, *args, **kwargs)
        return _wrapped
    return decorator
