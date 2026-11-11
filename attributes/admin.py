from django.contrib import admin
from django.db.models import Count

from .models import Attribute, EventAttributeValue


@admin.register(Attribute)
class AttributeAdmin(admin.ModelAdmin):
    list_display = ("name", "data_type", "usage_count")
    list_filter = ("data_type",)
    search_fields = ("name",)
    ordering = ("name",)

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(usage=Count("event_values"))

    @admin.display(description="events using it", ordering="usage")
    def usage_count(self, obj):
        return obj.usage


@admin.register(EventAttributeValue)
class EventAttributeValueAdmin(admin.ModelAdmin):
    list_display = ("event", "attribute", "attribute_type", "value")
    list_filter = ("attribute__data_type", "attribute")
    search_fields = ("event__title", "attribute__name")
    autocomplete_fields = ("attribute",)
    list_select_related = ("event", "attribute")
    ordering = ("event__title", "attribute__name")

    fieldsets = (
        (None, {"fields": ("event", "attribute")}),
        (
            "Value (fill exactly one, matching the attribute type)",
            {
                "fields": (
                    "value_string",
                    "value_integer",
                    "value_decimal",
                    "value_boolean",
                    "value_date",
                )
            },
        ),
    )

    @admin.display(description="type", ordering="attribute__data_type")
    def attribute_type(self, obj):
        return obj.attribute.data_type