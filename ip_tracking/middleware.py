from django.http import HttpResponseForbidden
from django.core.cache import cache
from ipware import get_client_ip
from ip_tracking.models import BlockedIP, RequestLog
from django_ip_geolocation.decorators import with_ip_geolocation
from django_ratelimit.middleware import RatelimitMiddleware
from django.conf import settings


class IPTrackingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.geolocator = with_ip_geolocation()

    def __call__(self, request):
        ip, _ = get_client_ip(request)

        if ip:
            # Check if IP is blocked
            if BlockedIP.objects.filter(ip_address=ip).exists():
                return HttpResponseForbidden("Your IP address has been blocked.")

            # Get geolocation data (from cache or API)
            cache_key = f"geo_{ip}"
            geo_data = cache.get(cache_key)

            if not geo_data:
                try:
                    geo_data = self.geolocator.get_geolocation(ip)
                    # Cache for 24 hours (86400 seconds)
                    cache.set(cache_key, geo_data, 86400)
                except Exception as e:
                    geo_data = {"country": None, "city": None}

            # Create log entry
            RequestLog.objects.create(
                ip_address=ip,
                path=request.path,
                method=request.method,
                country=geo_data.get("country"),
                city=geo_data.get("city"),
            )

        return self.get_response(request)


class CustomRateLimitMiddleware(RatelimitMiddleware):
    def get_rate_limit_key(self, request):
        if request.user.is_authenticated:
            return f"user:{request.user.pk}"
        return f'ip:{request.META.get("REMOTE_ADDR")}'

    def get_rate_limit_rate(self, request):
        if request.path == "/login/":  # Stricter limit for login
            return settings.RATELIMIT_RATES["login"]
        if request.user.is_authenticated:
            return settings.RATELIMIT_RATES["user"]
        return settings.RATELIMIT_RATES["anon"]
