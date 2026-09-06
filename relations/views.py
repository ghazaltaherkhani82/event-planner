from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from django.shortcuts import get_object_or_404

from .models import Registration, Feedback
from .serializers import RegistrationSerializer, FeedbackSerializer


class RegistrationListCreateView(generics.ListCreateAPIView):
    serializer_class = RegistrationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if getattr(user, 'is_organizer', False):
            return Registration.objects.filter(event__organizer=user)
        return Registration.objects.filter(participant=user)

    def perform_create(self, serializer):
        serializer.save(participant=self.request.user)


class FeedbackListCreateView(generics.ListCreateAPIView):
    serializer_class = FeedbackSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        queryset = Feedback.objects.all()
        event_id = self.request.query_params.get('event_id')
        if event_id:
            queryset = queryset.filter(event_id=event_id)
        return queryset

    def perform_create(self, serializer):
        serializer.save(participant=self.request.user)


class CancelRegistrationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, event_id):
        registration = get_object_or_404(Registration, event_id=event_id, participant=request.user)
        if registration.event.status in ['FINISHED', 'CANCELLED', 'Finished', 'Cancelled']:
            return Response(
                {"detail": "امکان انصراف از رویداد پایان‌یافته یا لغو‌شده وجود ندارد."},
                status=status.HTTP_400_BAD_REQUEST
            )
        registration.delete()
        return Response({"detail": "انصراف با موفقیت انجام شد."}, status=status.HTTP_200_OK)