from django.db import models


class RequestLog(models.Model):
    ip_address = models.CharField(max_length=45)
    timestamp = models.DateTimeField(auto_now_add=True)
    path = models.CharField(max_length=255)
    method = models.CharField(max_length=10, blank=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        ordering = ["-timestamp"]
        verbose_name = "Request Log"
        verbose_name_plural = "Request Logs"

    def __str__(self):
        location = (
            f"{self.city}, {self.country}"
            if self.city and self.country
            else "Unknown location"
        )
        return f"{self.ip_address} ({location}) - {self.method} {self.path}"


class BlockedIP(models.Model):
    ip_address = models.CharField(max_length=45, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    reason = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Blocked IP"
        verbose_name_plural = "Blocked IPs"

    def __str__(self):
        return f"{self.ip_address} (Blocked)"


class SuspiciousIP(models.Model):
    REASON_CHOICES = [
        ("HIGH_VOLUME", "High request volume"),
        ("SENSITIVE_PATHS", "Accessed sensitive paths"),
        ("MULTIPLE_REASONS", "Multiple suspicious activities"),
    ]

    ip_address = models.CharField(max_length=45)
    reason = models.CharField(max_length=20, choices=REASON_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    is_blocked = models.BooleanField(default=False)
    details = models.JSONField(default=dict, blank=True)

    class Meta:
        verbose_name = "Suspicious IP"
        verbose_name_plural = "Suspicious IPs"
        indexes = [
            models.Index(fields=["ip_address"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return f"{self.ip_address} - {self.get_reason_display()}"
