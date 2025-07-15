from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit
from django.views.decorators.http import require_POST
from django.conf import settings


class RateLimitExceededView(View):
    def get(self, request, *args, **kwargs):
        return JsonResponse(
            {"error": "Rate limit exceeded", "detail": "Please try again later."},
            status=429,
        )


# Apply this to your sensitive views
@method_decorator(
    ratelimit(key="user_or_ip", rate=settings.RATELIMIT_RATES["login"], method="POST"),
    name="dispatch",
)
class LoginView(View):
    def post(self, request, *args, **kwargs):
        # Your login logic here
        return JsonResponse({"status": "success"})


@require_POST
@ratelimit(key="ip", rate="5/m", method="POST")
def sensitive_api_view(request):
    was_limited = getattr(request, "limited", False)
    if was_limited:
        return JsonResponse({"error": "Too many requests"}, status=429)

    # Your view logic here
    return JsonResponse({"status": "success"})
