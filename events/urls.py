from django.urls import path
from .views import (
    EventListCreateView,
    EventDetailView,
    EventStatusUpdateView,
    EventStageListCreateView,
    EventResultListCreateView,
    EventConfirmedParticipantsView,
)

urlpatterns = [
    path('', EventListCreateView.as_view(), name='event-list-create'),
    path('<int:pk>/', EventDetailView.as_view(), name='event-detail'),
    path('<int:pk>/status/', EventStatusUpdateView.as_view(), name='event-status-update'),
    path('<int:event_id>/stages/', EventStageListCreateView.as_view(), name='event-stages'),
    path('<int:event_id>/results/', EventResultListCreateView.as_view(), name='event-results'),
    path('<int:event_id>/participants/', EventConfirmedParticipantsView.as_view(), name='event-participants'),
]