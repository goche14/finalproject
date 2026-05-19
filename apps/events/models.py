from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=255)

    slug = models.SlugField(
        unique=True
    )

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(
        max_length=100,
        unique=True
    )

    def __str__(self):
        return self.name


class Event(models.Model):

    class StatusChoices(models.TextChoices):
        DRAFT = "draft", "Draft"
        PUBLISHED = "published", "Published"
        CANCELLED = "cancelled", "Cancelled"

    class EventTypeChoices(models.TextChoices):
        ONLINE = "online", "Online"
        OFFLINE = "offline", "Offline"

    title = models.CharField(max_length=255)

    description = models.TextField()

    organizer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="organized_events"
    )

    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="events"
    )

    tags = models.ManyToManyField(
        Tag,
        blank=True,
        related_name="events"
    )

    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.DRAFT
    )

    event_type = models.CharField(
        max_length=20,
        choices=EventTypeChoices.choices
    )

    start_date = models.DateTimeField()

    end_date = models.DateTimeField()

    location = models.CharField(
        max_length=255,
        null=True,
        blank=True
    )

    max_attendees = models.PositiveIntegerField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    attendees = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through="Registration",
        related_name="events"
    )

    def __str__(self):
        return self.title


class Registration(models.Model):

    class RegistrationStatus(models.TextChoices):
        PENDING = "pending", "Pending"
        CONFIRMED = "confirmed", "Confirmed"
        CANCELLED = "cancelled", "Cancelled"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="registrations"
    )

    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name="registrations"
    )

    status = models.CharField(
        max_length=20,
        choices=RegistrationStatus.choices,
        default=RegistrationStatus.PENDING
    )

    registered_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        unique_together = ("user", "event")

    def __str__(self):
        return f"{self.user} -> {self.event}"


class Review(models.Model):

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reviews"
    )

    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name="reviews"
    )

    rating = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5)
        ]
    )

    comment = models.TextField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        unique_together = ("user", "event")

    def __str__(self):
        return f"Review by {self.user} for {self.event}"


class EventMedia(models.Model):

    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name="media"
    )

    file = models.ImageField(
        upload_to="event_media/"
    )

    uploaded_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"Media for {self.event.title}"