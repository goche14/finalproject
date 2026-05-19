from django.conf import settings
from django.db import models


class Notification(models.Model):

    class NotificationType(models.TextChoices):
        EVENT_CREATED = "event_created", "Event Created"
        EVENT_UPDATED = "event_updated", "Event Updated"
        EVENT_CANCELLED = "event_cancelled", "Event Cancelled"
        REGISTRATION_CONFIRMED = "registration_confirmed", "Registration Confirmed"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications"
    )

    notification_type = models.CharField(
        max_length=50,
        choices=NotificationType.choices
    )

    message = models.TextField()

    is_read = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"Notification for {self.user.username}"