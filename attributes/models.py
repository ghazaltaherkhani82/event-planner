from django.db import models
from django.core.exceptions import ValidationError
from events.models import Event


class Attribute(models.Model):
    class DataType(models.TextChoices):
        TEXT = 'TEXT', 'Text'
        INTEGER = 'INTEGER', 'Integer'
        BOOLEAN = 'BOOLEAN', 'Boolean'
        FLOAT = 'FLOAT', 'Float'

    name = models.CharField(max_length=100, unique=True)
    label = models.CharField(max_length=255)
    data_type = models.CharField(
        max_length=20,
        choices=DataType.choices,
        default=DataType.TEXT
    )
    description = models.TextField(blank=True, default='')

    def __str__(self):
        return f"{self.label} ({self.get_data_type_display()})"


class EventAttributeValue(models.Model):
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='attribute_values'
    )
    attribute = models.ForeignKey(
        Attribute,
        on_delete=models.CASCADE,
        related_name='event_values'
    )

    # Type-safe storage columns without using JSONField
    value_text = models.CharField(max_length=500, blank=True, null=True)
    value_int = models.IntegerField(blank=True, null=True)
    value_bool = models.BooleanField(blank=True, null=True)
    value_float = models.FloatField(blank=True, null=True)

    class Meta:
        unique_together = ('event', 'attribute')

    def __str__(self):
        return f"{self.event.title} -> {self.attribute.name}: {self.get_value()}"

    def get_value(self):
        """Returns the appropriate typed value based on attribute data type."""
        data_type = self.attribute.data_type
        if data_type == Attribute.DataType.INTEGER:
            return self.value_int
        elif data_type == Attribute.DataType.BOOLEAN:
            return self.value_bool
        elif data_type == Attribute.DataType.FLOAT:
            return self.value_float
        return self.value_text

    def set_value(self, val):
        """Sets the appropriate typed field based on the attribute data type."""
        data_type = self.attribute.data_type
        self.value_text = None
        self.value_int = None
        self.value_bool = None
        self.value_float = None

        if val is None:
            return

        try:
            if data_type == Attribute.DataType.INTEGER:
                self.value_int = int(val)
            elif data_type == Attribute.DataType.BOOLEAN:
                if isinstance(val, bool):
                    self.value_bool = val
                elif str(val).lower() in ['true', '1', 'yes']:
                    self.value_bool = True
                elif str(val).lower() in ['false', '0', 'no']:
                    self.value_bool = False
                else:
                    raise ValueError
            elif data_type == Attribute.DataType.FLOAT:
                self.value_float = float(val)
            else:
                self.value_text = str(val)
        except (ValueError, TypeError):
            raise ValidationError(
                f"Invalid value '{val}' provided for type {self.attribute.get_data_type_display()}."
            )

    def clean(self):
        super().clean()
        # Ensure that exactly the corresponding field is populated according to data_type
        val = self.get_value()
        if val is None:
            raise ValidationError(f"A valid value must be provided for attribute '{self.attribute.label}'.")