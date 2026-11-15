# ==================== results/admin.py ====================
from django.contrib import admin

from .models import EventResult, ResultEntry


class ResultEntryInline(admin.TabularInline):
    model = ResultEntry
    extra = 0


@admin.register(EventResult)
class EventResultAdmin(admin.ModelAdmin):
    list_display = ("id", "event", "is_published", "published_at")
    list_filter = ("is_published",)
    search_fields = ("event__title",)
    readonly_fields = ("published_at",)
    inlines = (ResultEntryInline,)


@admin.register(ResultEntry)
class ResultEntryAdmin(admin.ModelAdmin):
    list_display = ("id", "result", "entry_type", "label", "rank", "score")
    list_filter = ("entry_type",)
    search_fields = ("label", "participant__username", "result__event__title")