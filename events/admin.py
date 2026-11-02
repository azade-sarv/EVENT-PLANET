from django.contrib import admin

from .models import Event


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("title", "organizer", "status", "capacity", "start_time")
    list_filter = ("status",)
    search_fields = ("title",)