from django.contrib import admin
from .models import BlockedIP, RequestLog


@admin.register(BlockedIP)
class BlockedIPAdmin(admin.ModelAdmin):
    list_display = ("ip_address", "created_at", "reason")
    search_fields = ("ip_address", "reason")
    list_filter = ("created_at",)


@admin.register(RequestLog)
class RequestLogAdmin(admin.ModelAdmin):
    list_display = ("ip_address", "method", "path", "timestamp")
    list_filter = ("method", "timestamp")
    search_fields = ("ip_address", "path")
    readonly_fields = ("timestamp",)
