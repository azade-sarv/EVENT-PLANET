from django.contrib import admin

from .models import Attribute, EventAttributeValue


@admin.register(Attribute)
class AttributeAdmin(admin.ModelAdmin):
    list_display = ("name", "data_type")
    list_filter = ("data_type",)
    search_fields = ("name",)


@admin.register(EventAttributeValue)
class EventAttributeValueAdmin(admin.ModelAdmin):
    list_display = ("event_name", "attribute", "value")
    list_filter = ("attribute",)

    @admin.display(description="event")
    def event_name(self, obj):
        return obj.attribute.event
