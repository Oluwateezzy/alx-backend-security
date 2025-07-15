from django.http import HttpResponseForbidden
from ipware import get_client_ip
from ip_tracking.models import BlockedIP, RequestLog


class IPTrackingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Get client IP address
        ip, _ = get_client_ip(request)

        if ip:
            # Check if IP is blocked
            if BlockedIP.objects.filter(ip_address=ip).exists():
                return HttpResponseForbidden("Your IP address has been blocked.")

            # Log the request
            RequestLog.objects.create(
                ip_address=ip, path=request.path, method=request.method
            )

        return self.get_response(request)
