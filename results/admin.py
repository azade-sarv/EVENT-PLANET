from django.contrib import admin

from .models import EventResult, ResultEntry


class ResultEntryInline(admin.TabularInline):
    model = ResultEntry
    extra = 1
    fields = ("entry_type", "label", "participant", "rank", "score", "notes")


@admin.register(EventResult)
class EventResultAdmin(admin.ModelAdmin):
    list_display = ("event", "is_published", "published_at", "entries_count")
    list_filter = ("is_published",)
    inlines = [ResultEntryInline]

    @admin.display(description="Entries")
    def entries_count(self, obj):
        return obj.entries.count()