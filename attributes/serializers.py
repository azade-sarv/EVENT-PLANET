from datetime import date
from decimal import Decimal

from rest_framework import serializers

from events.models import Event
from .models import Attribute, EventAttributeValue, EventTypeAttribute


class AttributeSerializer(serializers.ModelSerializer):
    event_types = serializers.SerializerMethodField()

    class Meta:
        model = Attribute
        fields = ("id", "name", "data_type", "scope", "event", "event_types")
        read_only_fields = ("id", "scope", "event", "event_types")

    def get_event_types(self, obj):
        return [link.event_type for link in obj.event_type_links.all()]

    def validate_name(self, value):
        event = self.context.get("attribute_event")
        scope = (
            self.instance.scope
            if self.instance is not None
            else Attribute.Scope.EVENT
        )
        event_id = (
            self.instance.event_id
            if self.instance is not None
            else getattr(event, "pk", None)
        )

        queryset = Attribute.objects.filter(name=value, scope=scope)
        if scope == Attribute.Scope.EVENT:
            if event_id is None:
                raise serializers.ValidationError(
                    "An event is required for event-scoped attributes."
                )
            queryset = queryset.filter(event_id=event_id)
        else:
            queryset = queryset.filter(event__isnull=True)

        if self.instance is not None:
            queryset = queryset.exclude(pk=self.instance.pk)

        if queryset.exists():
            raise serializers.ValidationError(
                "An attribute with this name already exists in this scope."
            )

        return value

    def validate_data_type(self, value):
        if (
            self.instance is not None
            and value != self.instance.data_type
            and self.instance.event_values.exists()
        ):
            raise serializers.ValidationError(
                "Cannot change data_type while this attribute has values."
            )
        return value


class EventTypeAttributeSerializer(serializers.ModelSerializer):
    attribute_name = serializers.CharField(source="attribute.name", read_only=True)
    attribute = serializers.PrimaryKeyRelatedField(
        queryset=Attribute.objects.filter(scope=Attribute.Scope.GLOBAL)
    )

    class Meta:
        model = EventTypeAttribute
        fields = ("id", "event_type", "attribute", "attribute_name")
        read_only_fields = ("id",)


class TypedValueField(serializers.Field):
    def get_attribute(self, instance):
        return instance.value

    def to_representation(self, value):
        if isinstance(value, Decimal):
            return str(value)
        if isinstance(value, date):
            return value.isoformat()
        return value

    def to_internal_value(self, data):
        return data


class PublicEventAttributeValueSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="attribute.name", read_only=True)
    data_type = serializers.CharField(source="attribute.data_type", read_only=True)
    value = TypedValueField()

    class Meta:
        model = EventAttributeValue
        fields = ("name", "data_type", "value")


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
        if event.organizer_id != user.pk:
            raise serializers.ValidationError(
                "You can only set attributes for your own events."
            )
        return event

    def validate(self, attrs):
        attribute = attrs.get("attribute")
        if attribute is None and self.instance is not None:
            attribute = self.instance.attribute
        if attribute is None:
            raise serializers.ValidationError(
                {"attribute": "This field is required."}
            )

        if self.instance is not None and attribute.pk != self.instance.attribute_id:
            raise serializers.ValidationError(
                {
                    "attribute": (
                        "Attribute cannot be changed. Create a new value instead."
                    )
                }
            )

        event = attrs.get("event")
        if event is None and self.instance is not None:
            event = self.instance.event
        if event is None:
            raise serializers.ValidationError({"event": "This field is required."})

        if attribute.scope == Attribute.Scope.EVENT:
            if attribute.event_id != event.pk:
                raise serializers.ValidationError(
                    {"attribute": "This attribute belongs to another event."}
                )
        elif attribute.scope == Attribute.Scope.GLOBAL:
            if not EventTypeAttribute.objects.filter(
                attribute=attribute,
                event_type=event.event_type,
            ).exists():
                raise serializers.ValidationError(
                    {
                        "attribute": (
                            "This attribute is not enabled for this event type."
                        )
                    }
                )
        else:
            raise serializers.ValidationError(
                {"attribute": "This attribute has an invalid scope."}
            )

        existing_value = EventAttributeValue.objects.filter(
            event=event,
            attribute=attribute,
        )
        if self.instance is not None:
            existing_value = existing_value.exclude(pk=self.instance.pk)
        if existing_value.exists():
            raise serializers.ValidationError(
                {"attribute": "This attribute already has a value for this event."}
            )

        target_field = EventAttributeValue.VALUE_FIELDS.get(attribute.data_type)
        coercer = self.COERCERS.get(attribute.data_type)
        if target_field is None or coercer is None:
            raise serializers.ValidationError(
                {"attribute": "This attribute has an unsupported data type."}
            )

        if "value" in attrs:
            try:
                new_value = coercer.run_validation(attrs.pop("value"))
            except serializers.ValidationError as exc:
                raise serializers.ValidationError({"value": exc.detail}) from exc
        elif self.instance is not None:
            new_value = getattr(self.instance, target_field)
        else:
            raise serializers.ValidationError({"value": "This field is required."})

        for field in EventAttributeValue.VALUE_FIELDS.values():
            attrs[field] = None
        attrs[target_field] = new_value

        return attrs
