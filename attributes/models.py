from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q

from events.models import Event


class Attribute(models.Model):
    class DataType(models.TextChoices):
        STRING = "string", "String"
        INTEGER = "integer", "Integer"
        DECIMAL = "decimal", "Decimal"
        BOOLEAN = "boolean", "Boolean"
        DATE = "date", "Date"

    class Scope(models.TextChoices):
        GLOBAL = "global", "Global"
        EVENT = "event", "Event"

    name = models.CharField(max_length=100)
    data_type = models.CharField(max_length=20, choices=DataType.choices)
    scope = models.CharField(
        max_length=20,
        choices=Scope.choices,
        default=Scope.GLOBAL,
    )
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name="custom_attributes",
        null=True,
        blank=True,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["name"],
                condition=Q(scope="global"),
                name="unique_global_attribute_name",
            ),
            models.UniqueConstraint(
                fields=["event", "name"],
                condition=Q(scope="event"),
                name="unique_event_attribute_name",
            ),
            models.CheckConstraint(
                condition=(
                    Q(scope="global", event__isnull=True)
                    | Q(scope="event", event__isnull=False)
                ),
                name="attribute_scope_consistency",
            ),
        ]

    def __str__(self):
        if self.scope == self.Scope.EVENT:
            return f"{self.name} ({self.data_type}) @ event {self.event_id}"
        return f"{self.name} ({self.data_type})"

    def clean(self):
        errors = {}

        if self.scope == self.Scope.EVENT and self.event_id is None:
            errors["event"] = "Event-scoped attributes must belong to an event."

        if self.scope == self.Scope.GLOBAL and self.event_id is not None:
            errors["event"] = "Global attributes cannot be tied to an event."

        if errors:
            raise ValidationError(errors)


class EventTypeAttribute(models.Model):
    event_type = models.CharField(
        max_length=20,
        choices=Event.EventType.choices,
    )
    attribute = models.ForeignKey(
        Attribute,
        on_delete=models.CASCADE,
        related_name="event_type_links",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["event_type", "attribute"],
                name="unique_attribute_per_event_type",
            )
        ]

    def __str__(self):
        return f"{self.event_type} -> {self.attribute.name}"


class EventAttributeValue(models.Model):
    VALUE_FIELDS = {
        "string": "value_string",
        "integer": "value_integer",
        "decimal": "value_decimal",
        "boolean": "value_boolean",
        "date": "value_date",
    }

    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name="attribute_values",
    )
    attribute = models.ForeignKey(
        Attribute,
        on_delete=models.PROTECT,
        related_name="event_values",
    )

    value_string = models.CharField(max_length=255, null=True, blank=True)
    value_integer = models.IntegerField(null=True, blank=True)
    value_decimal = models.DecimalField(
        max_digits=12, decimal_places=4, null=True, blank=True
    )
    value_boolean = models.BooleanField(null=True, blank=True)
    value_date = models.DateField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["event", "attribute"],
                name="unique_attribute_per_event",
            )
        ]

    def __str__(self):
        return f"{self.event} | {self.attribute.name} = {self.value}"

    @property
    def value(self):
        field = self.VALUE_FIELDS[self.attribute.data_type]
        return getattr(self, field)

    def clean(self):
        if not self.attribute_id:
            return

        expected_field = self.VALUE_FIELDS[self.attribute.data_type]

        filled_fields = [
            field
            for field in self.VALUE_FIELDS.values()
            if getattr(self, field) is not None
        ]

        if filled_fields != [expected_field]:
            raise ValidationError(
                f"Exactly one value is required, in '{expected_field}' "
                f"(attribute type: {self.attribute.data_type})."
            )

        if (
            self.attribute.scope == Attribute.Scope.EVENT
            and self.attribute.event_id != self.event_id
        ):
            raise ValidationError(
                {"attribute": "This attribute belongs to another event."}
            )