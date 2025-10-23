from django.db import models, transaction
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from datetime import timedelta

class EventManager(models.Manager):
    def published(self):
        return self.filter(is_published=True)


    def upcoming(self):
        return self.filter(is_published=True, date_time__gte=timezone.now())

    
    def published_upcoming(self):
        return self.filter(is_published=True, date_time__gte=timezone.now() - timedelta(seconds=1))

    
    def all_events(self):
        return self.filter(is_published=True)

class PublishedEventManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_published=True, date_time__gte=timezone.now())

class Event(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    date_time = models.DateTimeField()
    location = models.CharField(max_length=255)
    is_published = models.BooleanField(default=False)
    max_capacity = models.PositiveIntegerField()
    booked_by = models.ManyToManyField(User, related_name='booked_events', blank=True)

    objects = EventManager()
    published = PublishedEventManager()

    def __str__(self):
        return self.title

    @property
    def available_quantity(self):
        """
        Returns the total remaining tickets across all ticket types for this event.
        """
        return sum(ticket.quantity_available for ticket in self.ticket_types.all())


class TicketType(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='ticket_types')
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    quantity_available = models.PositiveIntegerField()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['event', 'name'], name='unique_event_ticket_name')
        ]
        verbose_name = 'Ticket Type'
        verbose_name_plural = 'Ticket Types'

    def __str__(self):
        return f"{self.name} - {self.event.title}"


from django.db import models, transaction
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.contrib.auth.models import User

class Booking(models.Model):
    event = models.ForeignKey("Event", on_delete=models.CASCADE, related_name="bookings")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bookings")
    ticket_type = models.ForeignKey("TicketType", on_delete=models.CASCADE, related_name="bookings")
    quantity = models.PositiveIntegerField()
    booking_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user.username} booked {self.quantity} for {self.event.title}"

    @classmethod
    def create_booking(cls, user, ticket_type, quantity):
        """
        Safely create a booking with quantity check and auto quantity update.
        """
        with transaction.atomic():
            ticket = (
                ticket_type.__class__.objects
                .select_for_update()
                .get(pk=ticket_type.pk)
            )

            if ticket.quantity_available < quantity:
                raise ValidationError("Not enough tickets available for this type.")

            ticket.quantity_available -= quantity
            ticket.save()

            booking = cls.objects.create(
                event=ticket.event,
                user=user,
                ticket_type=ticket,
                quantity=quantity,
            )

            if hasattr(booking.event, 'booked_by'):
                booking.event.booked_by.add(user)
                
            return booking

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
