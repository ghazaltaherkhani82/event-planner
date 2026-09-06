from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Q
from .models import Event, EventStage, EventResult
from .serializers import EventSerializer, EventStageSerializer, EventResultSerializer
from relations.models import Registration


class IsOrganizerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.organizer == request.user or request.user.is_superuser


class EventListCreateView(generics.ListCreateAPIView):
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        user = self.request.user
        draft_values = [Event.Status.DRAFT, 'DRAFT', 'Draft']
        
        if user.is_authenticated and (user.is_superuser or getattr(user, 'role', '') == 'ORGANIZER' or getattr(user, 'is_organizer', False)):
            return Event.objects.filter(
                Q(organizer=user) | ~Q(status__in=draft_values)
            ).distinct().order_by('-created_at')
            
        return Event.objects.exclude(status__in=draft_values).order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(organizer=self.request.user)


class EventDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [IsOrganizerOrReadOnly]


class EventStatusUpdateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        event = get_object_or_404(Event, pk=pk)
        if event.organizer != request.user and not request.user.is_superuser:
            return Response(
                {"detail": "فقط برگزارکننده رویداد اجازه تغییر وضعیت را دارد."},
                status=status.HTTP_403_FORBIDDEN
            )

        new_status = request.data.get('status')

        normalized_map = {
            'DRAFT': Event.Status.DRAFT,
            'Draft': Event.Status.DRAFT,
            'PUBLISHED': Event.Status.PUBLISHED,
            'Published': Event.Status.PUBLISHED,
            'REGISTRATION_CLOSED': Event.Status.CLOSED,
            'CLOSED': Event.Status.CLOSED,
            'Closed': Event.Status.CLOSED,
            'FINISHED': Event.Status.FINISHED,
            'Finished': Event.Status.FINISHED,
            'CANCELLED': Event.Status.CANCELLED,
            'Cancelled': Event.Status.CANCELLED,
        }

        target_status = normalized_map.get(new_status, new_status)

        try:
            event.transition_to(target_status)
        except Exception as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            {"status": event.status, "detail": "وضعیت با موفقیت به‌روزرسانی شد."},
            status=status.HTTP_200_OK
        )


class EventStageListCreateView(generics.ListCreateAPIView):
    serializer_class = EventStageSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        return EventStage.objects.filter(event_id=self.kwargs['event_id']).order_by('order')

    def perform_create(self, serializer):
        event = get_object_or_404(Event, pk=self.kwargs['event_id'])
        if event.organizer != self.request.user and not self.request.user.is_superuser:
            raise permissions.exceptions.PermissionDenied("فقط برگزارکننده اجازه تعریف مرحله را دارد.")
        serializer.save(event=event)


class EventResultListCreateView(generics.ListCreateAPIView):
    serializer_class = EventResultSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        return EventResult.objects.filter(event_id=self.kwargs['event_id']).order_by('rank', '-score')

    def perform_create(self, serializer):
        event = get_object_or_404(Event, pk=self.kwargs['event_id'])
        if event.organizer != self.request.user and not self.request.user.is_superuser:
            raise permissions.exceptions.PermissionDenied("فقط برگزارکننده اجازه ثبت نمره را دارد.")

        participant_id = self.request.data.get('participant')
        
        # اگر قبلاً برای این کاربر نمره ثبت شده بود، همان رکورد به‌روزرسانی شود
        existing_result = EventResult.objects.filter(event=event, participant_id=participant_id).first()
        if existing_result:
            serializer.instance = existing_result
            
        serializer.save(event=event)


class EventConfirmedParticipantsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, event_id):
        event = get_object_or_404(Event, pk=event_id)
        if event.organizer != request.user and not request.user.is_superuser:
            return Response({"detail": "دسترسی غیرمجاز."}, status=status.HTTP_403_FORBIDDEN)
        
        regs = Registration.objects.filter(event=event, status='CONFIRMED').select_related('participant')
        participants = [
            {
                "id": r.participant.id,
                "username": r.participant.username,
            }
            for r in regs
        ]
        return Response(participants, status=status.HTTP_200_OK)