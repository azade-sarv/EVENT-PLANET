from datetime import date
from decimal import Decimal

from rest_framework import serializers

from events.models import Event
from .models import Attribute, EventTypeAttribute, EventAttributeValue


class AttributeSerializer(serializers.ModelSerializer):
    event_types = serializers.SerializerMethodField()

    class Meta:
        model = Attribute
        fields = ("id", "name", "data_type", "scope", "event", "event_types")
        read_only_fields = ("id",)

    def get_event_types(self, obj):
        return list(obj.event_type_links.values_list("event_type", flat=True))

    def validate_event(self, event):
        user = self.context["request"].user
        if event.organizer != user:
            raise serializers.ValidationError(
                "You can only set attributes for your own events."
            )
        return event


class EventTypeAttributeSerializer(serializers.ModelSerializer):
    attribute_name = serializers.CharField(source="attribute.name", read_only=True)

    class Meta:
        model = EventTypeAttribute
        fields = ("id", "event_type", "attribute", "attribute_name")
        read_only_fields = ("id",)


class TypedValueField(serializers.Field):
    def get_attribute(self, instance):
        return instance.value

    def to_representation(self, value):
        if isinstance(value, Decimal):
            return float(value)
        if isinstance(value, date):
            return value.isoformat()
        return value

    def to_internal_value(self, data):
        return data


class EventAttributeValueSerializer(serializers.ModelSerializer):
    COERCERS = {
        Attribute.DataType.STRING: serializers.CharField(max_length=255),
        Attribute.DataType.INTEGER: serializers.IntegerField(),
        Attribute.DataType.DECIMAL: serializers.DecimalField(
            max_digits=12, decimal_places=4
        ),
        Attribute.DataType.BOOLEAN: serializers.BooleanField(),
        Attribute.DataType.DATE: serializers.DateField(),
    }

    event = serializers.PrimaryKeyRelatedField(queryset=Event.objects.all())
    attribute = serializers.PrimaryKeyRelatedField(queryset=Attribute.objects.all())
    attribute_name = serializers.CharField(source="attribute.name", read_only=True)
    data_type = serializers.CharField(source="attribute.data_type", read_only=True)
    value = TypedValueField()

    class Meta:
        model = EventAttributeValue
        fields = (
            "id",
            "event",
            "attribute",
            "attribute_name",
            "data_type",
            "value",
        )
        read_only_fields = ("id",)

    def validate_event(self, event):
        user = self.context["request"].user
        if event.organizer != user:
            raise serializers.ValidationError(
                "You can only set attributes for your own events."
            )
        return event

    def validate(self, attrs):
        attribute = attrs.get("attribute") or getattr(self.instance, "attribute", None)
        if attribute is None:
            raise serializers.ValidationError({"attribute": "This field is required."})

        if self.instance is not None and attribute != self.instance.attribute:
            raise serializers.ValidationError(
                {"attribute": "Attribute cannot be changed. Create a new value instead."}
            )

        event = attrs.get("event") or getattr(self.instance, "event", None)
        if event is None:
            raise serializers.ValidationError({"event": "This field is required."})

        qs = EventAttributeValue.objects.filter(event=event, attribute=attribute)
        if self.instance is not None:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError(
                {"attribute": "This attribute already has a value for this event."}
            )

        target_field = EventAttributeValue.VALUE_FIELDS[attribute.data_type]

        if "value" in attrs:
            try:
                new_value = self.COERCERS[attribute.data_type].run_validation(
                    attrs.pop("value")
                )
            except serializers.ValidationError as exc:
                raise serializers.ValidationError({"value": exc.detail})
        elif self.instance is not None:
            new_value = getattr(self.instance, target_field)
        else:
            raise serializers.ValidationError({"value": "This field is required."})

        for field in EventAttributeValue.VALUE_FIELDS.values():
            attrs[field] = None
        attrs[target_field] = new_value

        return attrs