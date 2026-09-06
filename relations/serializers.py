from rest_framework import serializers
from .models import Registration, Feedback
from events.models import Event


class RegistrationSerializer(serializers.ModelSerializer):
    participant_username = serializers.CharField(source='participant.username', read_only=True)
    event_title = serializers.CharField(source='event.title', read_only=True)

    class Meta:
        model = Registration
        fields = ['id', 'event', 'event_title', 'participant', 'participant_username', 'status', 'registered_at']
        read_only_fields = ['participant', 'registered_at']

    def validate(self, attrs):
        event = attrs.get('event')
        request = self.context.get('request')
        user = request.user if request else None

        if event.status != Event.Status.PUBLISHED:
            raise serializers.ValidationError("Registrations are only allowed for PUBLISHED events.")

        if Registration.objects.filter(event=event, participant=user).exists():
            raise serializers.ValidationError("You have already registered for this event.")

        confirmed_count = event.registrations.filter(status=Registration.Status.CONFIRMED).count()
        if confirmed_count >= event.capacity:
            raise serializers.ValidationError("This event has reached full capacity.")

        return attrs


class FeedbackSerializer(serializers.ModelSerializer):
    participant_username = serializers.CharField(source='participant.username', read_only=True)

    class Meta:
        model = Feedback
        fields = ['id', 'event', 'participant', 'participant_username', 'rating', 'comment', 'created_at']
        read_only_fields = ['participant', 'created_at']

    def validate(self, attrs):
        event = attrs.get('event')
        request = self.context.get('request')
        user = request.user if request else None

        if event.status != Event.Status.FINISHED:
            raise serializers.ValidationError("Feedback can only be submitted after the event has FINISHED.")

        has_registered = Registration.objects.filter(
            event=event,
            participant=user,
            status=Registration.Status.CONFIRMED
        ).exists()
        if not has_registered:
            raise serializers.ValidationError("Only participants who registered and attended can submit feedback.")

        if Feedback.objects.filter(event=event, participant=user).exists():
            raise serializers.ValidationError("You have already submitted feedback for this event.")

        return attrs