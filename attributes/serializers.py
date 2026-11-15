from rest_framework import serializers

from .models import Attribute, EventAttributeValue


class AttributeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attribute
        fields = ("id", "name", "data_type")
        read_only_fields = ("id",)


class EventAttributeValueSerializer(serializers.ModelSerializer):
    attribute_name = serializers.CharField(source="attribute.name", read_only=True)
    data_type = serializers.CharField(source="attribute.data_type", read_only=True)

    class Meta:
        model = EventAttributeValue
        fields = (
            "id",
            "event",
            "attribute",
            "attribute_name",
            "data_type",
            "value_string",
            "value_integer",
            "value_decimal",
            "value_boolean",
            "value_date",
        )
        read_only_fields = ("id", "attribute_name", "data_type")

    def validate_event(self, event):
        user = self.context["request"].user
        if event.organizer != user:
            raise serializers.ValidationError(
                "You can only set attributes for your own events."
            )
        return event

    def validate(self, attrs):
        attribute = attrs.get("attribute")
        event = attrs.get("event")

        qs = EventAttributeValue.objects.filter(event=event, attribute=attribute)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError(
                "This attribute already has a value for this event."
            )

        value_fields = [
            "value_string",
            "value_integer",
            "value_decimal",
            "value_boolean",
            "value_date",
        ]
        filled = [f for f in value_fields if attrs.get(f) is not None]
        if len(filled) != 1:
            raise serializers.ValidationError(
                "Exactly one value field must be filled."
            )

        return attrs