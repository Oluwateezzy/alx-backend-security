import os
from celery import Celery
from django.conf import settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ip_tracker.settings")

app = Celery("ip_tracker")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

app.conf.beat_schedule = {
    "detect-suspicious-ips-hourly": {
        "task": "ip_tracking.tasks.detect_suspicious_ips",
        "schedule": 3600.0,  # Every hour (in seconds)
    },
}
