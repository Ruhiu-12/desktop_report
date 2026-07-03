from django.core.exceptions import PermissionDenied
from functools import wraps

def role_required(allowed_roles=[]):
    """
    Decorator that checks if a user is in one of the allowed groups.
    Usage: @role_required(['analyst', 'investigator'])
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Allow superusers access to everything
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            
            # Check if user belongs to any of the allowed roles (groups)
            if request.user.groups.filter(name__in=allowed_roles).exists():
                return view_func(request, *args, **kwargs)
            
            # If not authorized, raise 403 Forbidden
            raise PermissionDenied
        return wrapper
    return decorator