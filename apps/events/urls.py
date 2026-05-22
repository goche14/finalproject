from rest_framework.routers import DefaultRouter
from rest_framework_nested.routers import NestedDefaultRouter

from .views import (
    EventViewSet,
    RegistrationViewSet,
    ReviewViewSet,
)

router = DefaultRouter()

router.register(r'events', EventViewSet)

events_router = NestedDefaultRouter(
    router,
    r'events',
    lookup='event'
)

events_router.register(
    r'registrations',
    RegistrationViewSet,
    basename='event-registrations'
)

events_router.register(
    r'reviews',
    ReviewViewSet,
    basename='event-reviews'
)

urlpatterns = []

urlpatterns += router.urls
urlpatterns += events_router.urls