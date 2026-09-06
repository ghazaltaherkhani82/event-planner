from rest_framework import serializers
from .models import Attribute, EventAttributeValue


class AttributeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attribute
        fields = ['id', 'name', 'label', 'data_type', 'description']


class EventAttributeValueSerializer(serializers.ModelSerializer):
    attribute_name = serializers.ReadOnlyField(source='attribute.name')
    attribute_label = serializers.ReadOnlyField(source='attribute.label')
    data_type = serializers.ReadOnlyField(source='attribute.data_type')
    value = serializers.SerializerMethodField()

    class Meta:
        model = EventAttributeValue
        fields = [
            'id', 'event', 'attribute', 'attribute_name',
            'attribute_label', 'data_type', 'value'
        ]
        read_only_fields = ['event']

    def get_value(self, obj):
        return obj.get_value()

    def create(self, validated_data):
        raw_val = self.initial_data.get('value')
        
        # مقداردهی به آبجکت به همراه فیلدهایی که ویو پاس می‌دهد (مثل event یا event_id)
        instance = EventAttributeValue(**validated_data)
        instance.set_value(raw_val)
        instance.full_clean()
        instance.save()
        return instance

    def update(self, instance, validated_data):
        # به‌روزرسانی فیلدهای مدل در صورت ارسال
        for attr, val in validated_data.items():
            setattr(instance, attr, val)

        if 'value' in self.initial_data:
            instance.set_value(self.initial_data.get('value'))
            
        instance.full_clean()
        instance.save()
        return instance