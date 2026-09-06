from rest_framework import generics
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from accounts.permissions import IsOrganizer
from .models import Attribute, EventAttributeValue
from .serializers import AttributeSerializer, EventAttributeValueSerializer


class AttributeListCreateView(generics.ListCreateAPIView):
    queryset = Attribute.objects.all()
    serializer_class = AttributeSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsOrganizer()]
        return [IsAuthenticatedOrReadOnly()]


class AttributeDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Attribute.objects.all()
    serializer_class = AttributeSerializer

    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [IsOrganizer()]
        return [IsAuthenticatedOrReadOnly()]


class EventAttributeValueListCreateView(generics.ListCreateAPIView):
    serializer_class = EventAttributeValueSerializer

    def get_queryset(self):
        event_id = self.kwargs.get('event_id')
        return EventAttributeValue.objects.filter(event_id=event_id)

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsOrganizer()]
        return [IsAuthenticatedOrReadOnly()]

    def perform_create(self, serializer):
        serializer.save(event_id=self.kwargs.get('event_id'))


class EventAttributeValueDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = EventAttributeValueSerializer
    lookup_field = 'attribute_id'

    def get_queryset(self):
        event_id = self.kwargs.get('event_id')
        return EventAttributeValue.objects.filter(event_id=event_id)

    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [IsOrganizer()]
        return [IsAuthenticatedOrReadOnly()]