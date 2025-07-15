from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from ip_tracking.models import RequestLog, SuspiciousIP, BlockedIP


@shared_task(bind=True)
def detect_suspicious_ips(self):
    # Time range for analysis (last hour)
    one_hour_ago = timezone.now() - timedelta(hours=1)

    # 1. Detect high volume IPs (>100 requests/hour)
    high_volume_ips = (
        RequestLog.objects.filter(timestamp__gte=one_hour_ago)
        .values("ip_address")
        .annotate(request_count=models.Count("id"))
        .filter(request_count__gt=100)
    )

    for entry in high_volume_ips:
        SuspiciousIP.objects.update_or_create(
            ip_address=entry["ip_address"],
            defaults={
                "reason": "HIGH_VOLUME",
                "details": {
                    "request_count": entry["request_count"],
                    "time_window": "1 hour",
                },
                "is_blocked": False,
            },
        )

    # 2. Detect access to sensitive paths
    sensitive_paths = ["/admin/", "/login/", "/api/auth/"]
    sensitive_access = (
        RequestLog.objects.filter(timestamp__gte=one_hour_ago, path__in=sensitive_paths)
        .values("ip_address", "path")
        .annotate(access_count=models.Count("id"))
        .filter(access_count__gt=3)  # More than 3 accesses to sensitive paths
    )

    for entry in sensitive_access:
        SuspiciousIP.objects.update_or_create(
            ip_address=entry["ip_address"],
            defaults={
                "reason": "SENSITIVE_PATHS",
                "details": {
                    "path": entry["path"],
                    "access_count": entry["access_count"],
                },
                "is_blocked": False,
            },
        )

    return f"Detected {len(high_volume_ips)} high volume IPs and {len(sensitive_access)} sensitive path accesses"
