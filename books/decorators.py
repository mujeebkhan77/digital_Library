from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def admin_required(view_func):
    """Decorator to check if user is admin"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Please login to access this page.')
            return redirect('login')
        if request.user.role != 'admin':
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('home')
        return view_func(request, *args, **kwargs)
    return wrapper

