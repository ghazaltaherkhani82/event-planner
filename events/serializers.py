from rest_framework import serializers
from .models import Event, EventStage, EventResult


class EventStageSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventStage
        fields = [
            'id', 'event', 'title', 'description', 'order',
            'capacity', 'start_time', 'end_time', 'stage_roles'
        ]
        read_only_fields = ['event']


class EventResultSerializer(serializers.ModelSerializer):
    participant_name = serializers.ReadOnlyField(source='participant.username')

    class Meta:
        model = EventResult
        fields = [
            'id', 'event', 'participant', 'participant_name',
            'score', 'rank', 'remarks', 'published_at'
        ]
        read_only_fields = ['event', 'published_at']


class EventSerializer(serializers.ModelSerializer):
    organizer_name = serializers.ReadOnlyField(source='organizer.username')
    registered_count = serializers.SerializerMethodField()
    remaining_capacity = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = [
            'id', 'title', 'description', 'capacity',
            'registered_count', 'remaining_capacity',
            'start_time', 'end_time', 'status',
            'organizer', 'organizer_name', 'created_at', 'updated_at'
        ]
        read_only_fields = ['organizer', 'created_at', 'updated_at']

    def get_registered_count(self, obj):
        return obj.registrations.filter(status='CONFIRMED').count()

    def get_remaining_capacity(self, obj):
        if obj.capacity is None:
            return None
        confirmed = obj.registrations.filter(status='CONFIRMED').count()
        return max(0, obj.capacity - confirmed)

    def create(self, validated_data):
        validated_data['organizer'] = self.context['request'].user
        return super().create(validated_data)


class EventStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ['status']

    def update(self, instance, validated_data):
        new_status = validated_data.get('status')
        instance.transition_to(new_status)
        return instance