from functools import wraps

from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied
from django.views import View


def is_manager(user):
    return user.is_authenticated and user.is_active and user.is_staff


class ManagerRequiredMixin:
    """Anonymous users go to the login page; logged-in users without staff access get 403."""

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect_to_login(request.get_full_path(), '/manage/login/')
        if not is_manager(request.user):
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


def manager_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect_to_login(request.get_full_path(), '/manage/login/')
        if not is_manager(request.user):
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
    return wrapper
