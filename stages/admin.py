from django.contrib import admin

from django.contrib import admin

from .models import Stage, StageRole


class StageRoleInline(admin.TabularInline):
    model = StageRole
    extra = 1


@admin.register(Stage)
class StageAdmin(admin.ModelAdmin):
    list_display = ("title", "event", "order", "start_time", "end_time")
    list_filter = ("event",)
    inlines = [StageRoleInline]