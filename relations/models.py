from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from events.models import Event


class Registration(models.Model):
    class Status(models.TextChoices):
        CONFIRMED = 'CONFIRMED', 'Confirmed'
        CANCELLED = 'CANCELLED', 'Cancelled'

    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='registrations'
    )
    participant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='event_registrations'
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.CONFIRMED
    )
    registered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('event', 'participant')
        ordering = ['-registered_at']

    def __str__(self):
        return f"{self.participant.username} -> {self.event.title} ({self.status})"

    def clean(self):
        super().clean()
        # 1. Event must be in PUBLISHED status
        if self.event.status != Event.Status.PUBLISHED:
            raise ValidationError("Registrations are only allowed for PUBLISHED events.")

        # 2. Check capacity only for new confirmed registrations
        if not self.pk and self.status == self.Status.CONFIRMED:
            current_active_count = self.event.registrations.filter(
                status=self.Status.CONFIRMED
            ).count()
            if current_active_count >= self.event.capacity:
                raise ValidationError("Event has reached its maximum capacity limit.")


class Feedback(models.Model):
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='feedbacks'
    )
    participant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='event_feedbacks'
    )
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Rating between 1 and 5"
    )
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('event', 'participant')
        ordering = ['-created_at']

    def __str__(self):
        return f"Feedback: {self.event.title} - {self.participant.username} ({self.rating}/5)"

    def clean(self):
        super().clean()
        # 1. Event must be in FINISHED status
        if self.event.status != Event.Status.FINISHED:
            raise ValidationError("Feedback can only be submitted after the event has FINISHED.")

        # 2. User must have an active confirmed registration for this event
        has_registered = Registration.objects.filter(
            event=self.event,
            participant=self.participant,
            status=Registration.Status.CONFIRMED
        ).exists()
        if not has_registered:
            raise ValidationError("Only registered participants are allowed to submit feedback.")
        