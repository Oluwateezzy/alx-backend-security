from django.core.management.base import BaseCommand
from ip_tracking.models import BlockedIP


class Command(BaseCommand):
    help = "Add an IP address to the blocklist"

    def add_arguments(self, parser):
        parser.add_argument("ip_address", type=str, help="IP address to block")
        parser.add_argument(
            "--reason", type=str, help="Reason for blocking", default=""
        )

    def handle(self, *args, **options):
        ip_address = options["ip_address"]
        reason = options["reason"]

        try:
            BlockedIP.objects.create(ip_address=ip_address, reason=reason)
            self.stdout.write(
                self.style.SUCCESS(f"Successfully blocked IP: {ip_address}")
            )
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error blocking IP: {str(e)}"))
