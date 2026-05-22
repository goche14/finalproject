# apps/events/views.py

from django.shortcuts import get_object_or_404
from django.db.models import Count, Avg

from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import (
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
)

from django_filters.rest_framework import DjangoFilterBackend

from .models import (
    Event,
    Registration,
    Review,
    Category,
    Tag,
    EventMedia,
)

from .serializers import (
    EventSerializer,
    RegistrationSerializer,
    ReviewSerializer,
    CategorySerializer,
    TagSerializer,
    EventMediaSerializer,
)

from .permissions import (
    IsOrganizer,
    IsOwnerOrReadOnly,
    IsConfirmedAttendee,
)

from .filters import EventFilter


# =========================
# EVENT VIEWSET
# =========================

class EventViewSet(viewsets.ModelViewSet):

    queryset = Event.objects.all().select_related(
        'organizer',
        'category'
    ).prefetch_related(
        'tags'
    )

    serializer_class = EventSerializer

    permission_classes = [IsAuthenticatedOrReadOnly]

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    filterset_class = EventFilter

    search_fields = [
        'title',
        'description',
    ]

    ordering_fields = [
        'start_date',
        'created_at',
    ]

    ordering = ['-created_at']

    def get_permissions(self):

        if self.action == 'create':
            return [IsOrganizer()]

        if self.action in [
            'update',
            'partial_update',
            'destroy'
        ]:
            return [IsOwnerOrReadOnly()]

        return super().get_permissions()

    def perform_create(self, serializer):

        serializer.save(
            organizer=self.request.user
        )

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated]
    )
    def stats(self, request):

        total_events = Event.objects.count()

        published_events = Event.objects.filter(
            status='published'
        ).count()

        total_registrations = Registration.objects.count()

        events_by_status = (
            Event.objects
            .values('status')
            .annotate(count=Count('id'))
        )

        top_events = (
            Event.objects
            .annotate(
                registration_count=Count('registration'),
                avg_rating=Avg('review__rating')
            )
            .order_by('-registration_count')[:5]
        )

        data = {
            'total_events': total_events,
            'published_events': published_events,
            'total_registrations': total_registrations,
            'events_by_status': events_by_status,
            'top_events': [
                {
                    'id': event.id,
                    'title': event.title,
                    'registration_count': event.registration_count,
                    'avg_rating': event.avg_rating,
                }
                for event in top_events
            ]
        }

        return Response(data)


# =========================
# REGISTRATION VIEWSET
# =========================

class RegistrationViewSet(viewsets.ModelViewSet):

    serializer_class = RegistrationSerializer

    permission_classes = [IsAuthenticated]

    def get_queryset(self):

        event_id = self.kwargs.get('event_pk')

        return Registration.objects.filter(
            event_id=event_id
        ).select_related(
            'user',
            'event'
        )

    def perform_create(self, serializer):

        event_id = self.kwargs.get('event_pk')

        event = get_object_or_404(
            Event,
            id=event_id
        )

        confirmed_count = Registration.objects.filter(
            event=event,
            status='confirmed'
        ).count()

        if confirmed_count >= event.max_attendees:

            return Response(
                {
                    'detail': 'Event is full.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        already_registered = Registration.objects.filter(
            user=self.request.user,
            event=event
        ).exists()

        if already_registered:

            return Response(
                {
                    'detail': 'Already registered.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer.save(
            user=self.request.user,
            event=event,
            status='pending'
        )


# =========================
# REVIEW VIEWSET
# =========================

class ReviewViewSet(viewsets.ModelViewSet):

    serializer_class = ReviewSerializer

    permission_classes = [
        IsAuthenticated,
        IsConfirmedAttendee,
    ]

    def get_queryset(self):

        event_id = self.kwargs.get('event_pk')

        return Review.objects.filter(
            event_id=event_id
        ).select_related(
            'user',
            'event'
        )

    def perform_create(self, serializer):

        event_id = self.kwargs.get('event_pk')

        event = get_object_or_404(
            Event,
            id=event_id
        )

        serializer.save(
            user=self.request.user,
            event=event
        )


# =========================
# CATEGORY VIEWSET
# =========================

class CategoryViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = Category.objects.all()

    serializer_class = CategorySerializer


# =========================
# TAG VIEWSET
# =========================

class TagViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = Tag.objects.all()

    serializer_class = TagSerializer


# =========================
# EVENT MEDIA VIEWSET
# =========================

class EventMediaViewSet(viewsets.ModelViewSet):

    serializer_class = EventMediaSerializer

    permission_classes = [IsAuthenticated]

    def get_queryset(self):

        event_id = self.kwargs.get('event_pk')

        return EventMedia.objects.filter(
            event_id=event_id
        )

    def perform_create(self, serializer):

        event_id = self.kwargs.get('event_pk')

        event = get_object_or_404(
            Event,
            id=event_id
        )

        serializer.save(event=event)