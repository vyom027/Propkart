from django.shortcuts import redirect
from functools import wraps
from django.contrib import messages

def modal_login_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.info(request, "Please log in to continue.")
            return redirect('/')
        return view_func(request, *args, **kwargs)
    return _wrapped_view