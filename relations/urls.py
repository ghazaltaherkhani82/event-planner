from django.urls import path
from .views import (
    RegistrationListCreateView,
    FeedbackListCreateView,
    CancelRegistrationView,
)

app_name = 'relations'

urlpatterns = [
    path('registrations/', RegistrationListCreateView.as_view(), name='registration-list-create'),
    path('feedbacks/', FeedbackListCreateView.as_view(), name='feedback-list-create'),
    path('events/<int:event_id>/cancel/', CancelRegistrationView.as_view(), name='cancel-registration'),
]