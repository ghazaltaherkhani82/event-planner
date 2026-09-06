from django.urls import path
from .views import (
    AttributeListCreateView,
    AttributeDetailView,
    EventAttributeValueListCreateView,
    EventAttributeValueDetailView
)

app_name = 'attributes'

urlpatterns = [
    path('definitions/', AttributeListCreateView.as_view(), name='attribute-list-create'),
    path('definitions/<int:pk>/', AttributeDetailView.as_view(), name='attribute-detail'),
    path('events/<int:event_id>/', EventAttributeValueListCreateView.as_view(), name='event-attributes-list-create'),
    path('events/<int:event_id>/<int:attribute_id>/', EventAttributeValueDetailView.as_view(), name='event-attribute-detail'),
]