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

    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name="attributes",
        default=None,
    )
    name = models.CharField(max_length=100)
    data_type = models.CharField(
        max_length=20,
        choices=DataType.choices,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["event", "name"],
                name="unique_attribute_name_per_event",
            )
        ]

    def __str__(self):
        return f"{self.event.title} - {self.name}"


class EventAttributeValue(models.Model):
    VALUE_FIELDS = {
        "string": "value_string",
        "integer": "value_integer",
        "decimal": "value_decimal",
        "boolean": "value_boolean",
        "date": "value_date",
    }

    attribute = models.OneToOneField(
        Attribute,
        on_delete=models.CASCADE,
        related_name="value",
    )

    value_string = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )
    value_integer = models.IntegerField(null=True, blank=True)
    value_decimal = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        null=True,
        blank=True,
    )
    value_boolean = models.BooleanField(null=True, blank=True)
    value_date = models.DateField(null=True, blank=True)

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
                f"Only {expected_field} must contain a value."
            )