from django.contrib import admin

# import models
from hostlock.models import (Host, Lock)


class HostAdmin(admin.ModelAdmin):
    list_display = ("id", "hostname", "owner", "is_locked", "updated_at")
    search_fields = ["hostname", "owner__username"]
    list_filter = ["is_locked"]


class LockAdmin(admin.ModelAdmin):
    list_display = ("id", "host", "requester", "source", "status", "expiration", "updated_at")
    search_fields = ["host", "requester", "status"]
    list_filter = ["status"]


# Register your models here.
admin.site.register(Host, HostAdmin)
admin.site.register(Lock, LockAdmin)
