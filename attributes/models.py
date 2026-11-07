from django.core.exceptions import ValidationError
from django.db import models

from events.models import Event


class Attribute(models.Model):
    class DataType(models.TextChoices):
        STRING = "string", "String"
        INTEGER = "integer", "Integer"
        DECIMAL = "decimal", "Decimal"
        BOOLEAN = "boolean", "Boolean"
        DATE = "date", "Date"

    name = models.CharField(max_length=100, unique=True)
    data_type = models.CharField(max_length=20, choices=DataType.choices)

    def __str__(self):
        return f"{self.name} ({self.data_type})"


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
        return getattr(self, self.VALUE_FIELDS[self.attribute.data_type])

    def clean(self):
        if not self.attribute_id:
            return
        expected = self.VALUE_FIELDS[self.attribute.data_type]
        filled = [
            f for f in self.VALUE_FIELDS.values() if getattr(self, f) is not None
        ]
        if filled != [expected]:
            raise ValidationError(
                f"Exactly one value is required, in '{expected}' "
                f"(attribute type: {self.attribute.data_type})."
            )