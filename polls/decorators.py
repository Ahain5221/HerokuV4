from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect


def stuff_or_superuser_required(view_func):
    def decorator(request, *args, **kwargs):
        print("Dekorator stuff or super")
        if request.user.is_superuser or request.user.is_staff:
            return view_func(request, *args, **kwargs)
        return redirect('index')
    return decorator


def anonymous_required(view_func):
    def decorator(request, *args, **kwargs,):
        if not request.user.is_authenticated:
            return view_func(request, *args, **kwargs)
        return redirect('index')
    return decorator

