from django.test import TestCase
from django.core.exceptions import ValidationError
from django.utils import timezone
from events.models import Event, TicketType
from django.contrib.auth.models import User

class EventModelAndFieldTests(TestCase):

    def test_max_capacity_allows_positive_integer(self):
        """Test that max_capacity accepts valid positive values"""
        event = Event(
            title='Sample Event',
            location='Main Hall',
            date_time=timezone.now(),
            is_published=True,
            max_capacity=100
        )
        event.full_clean()
        event.save()
        self.assertEqual(event.max_capacity, 100)

    def test_max_capacity_cannot_be_negative(self):
        """Test that max_capacity does not accept negative values"""
        event = Event(
            title='Invalid Event',
            location='Main Hall',
            date_time=timezone.now(),
            is_published=False,
            max_capacity=-10
        )
        with self.assertRaises(ValidationError):
            event.full_clean()

    def test_max_capacity_zero_is_valid(self):
        """Test that max_capacity can be zero"""
        event = Event(
            title='Zero Capacity Event',
            location='Empty Hall',
            date_time=timezone.now(),
            is_published=False,
            max_capacity=0
        )
        event.full_clean()
        self.assertEqual(event.max_capacity, 0)

    def test_is_published_default_value(self):
        """Check that is_published defaults to False"""
        event = Event.objects.create(
            title='Test Event',
            location='Test Hall',
            date_time=timezone.now(),
            max_capacity=100
        )
        self.assertFalse(event.is_published)

    def test_title_cannot_be_blank(self):
        """Test that title cannot be blank"""
        event = Event(
            title='',
            location='Test Hall',
            date_time=timezone.now(),
            max_capacity=50
        )
        with self.assertRaises(ValidationError):
            event.full_clean()

    def test_title_max_length(self):
        """Test that title cannot exceed 255 characters"""
        long_title = 'A' * 256
        event = Event(
            title=long_title,
            location='Test Hall',
            date_time=timezone.now(),
            max_capacity=100
        )
        with self.assertRaises(ValidationError):
            event.full_clean()

    def test_description_can_be_blank(self):
        """Test that description can be blank (blank=True)"""
        event = Event.objects.create(
            title='No Description Event',
            location='Main Hall',
            date_time=timezone.now(),
            max_capacity=100
        )
        self.assertEqual(event.description, '')

    def test_booked_by_many_to_many_relationship(self):
        """Test that users can be added to booked_by"""
        user1 = User.objects.create_user(username='user1', password='testpass')
        user2 = User.objects.create_user(username='user2', password='testpass')

        event = Event.objects.create(
            title='Concert',
            location='Auditorium',
            date_time=timezone.now(),
            max_capacity=200
        )

        event.booked_by.add(user1, user2)

        self.assertEqual(event.booked_by.count(), 2)
        self.assertIn(user1, event.booked_by.all())
        self.assertIn(user2, event.booked_by.all())


class TicketTypeModelTest(TestCase):

    def setUp(self):
        self.event = Event.objects.create(
            title='Sample Event',
            location='Main Hall',
            date_time=timezone.now(),
            max_capacity=100
        )

    def test_tickettype_creation_and_fields(self):
        """Test that TicketType can be created with valid fields"""
        ticket = TicketType.objects.create(
            event=self.event,
            name='VIP Ticket',
            price=999.99,
            quantity_available=50
        )
        self.assertEqual(ticket.name, 'VIP Ticket')
        self.assertEqual(ticket.price, 999.99)
        self.assertEqual(ticket.quantity_available, 50)
        self.assertEqual(ticket.event, self.event)

    def test_tickettype_quantity_cannot_be_negative(self):
        """Test that quantity_available cannot be negative"""
        ticket = TicketType(
            event=self.event,
            name='Standard Ticket',
            price=499.99,
            quantity_available=-10
        )
        with self.assertRaises(ValidationError):
            ticket.full_clean()


class TicketTypeModelTest(TestCase):
    def setUp(self):
        """
        Create an Event instance for TicketType foreign key.
        """
        self.event = Event.objects.create(
            title='Music Concert',
            description='Live performance event',
            date_time=timezone.now(),
            location='Main Hall',
            is_published=True,
            max_capacity=500
        )

    def test_name_cannot_exceed_100_characters(self):
        """
        Ensure name cannot exceed max_length=100.
        """
        long_name = 'A' * 101
        ticket = TicketType(
            event=self.event,
            name=long_name,
            price=100.00,
            quantity_available=10
        )
        with self.assertRaises(ValidationError):
            ticket.full_clean()  # triggers field validation
            ticket.save()

    def test_price_cannot_be_negative(self):
        """
        Ensure price cannot be negative.
        """
        ticket = TicketType(
            event=self.event,
            name='VIP',
            price=-50.00,
            quantity_available=10
        )
        with self.assertRaises(ValidationError):
            ticket.full_clean()

    def test_quantity_cannot_be_negative(self):
        """
        Ensure quantity_available cannot be negative.
        """
        ticket = TicketType(
            event=self.event,
            name='Standard',
            price=100.00,
            quantity_available=-5
        )
        with self.assertRaises(ValidationError):
            ticket.full_clean()

    def test_ticket_deleted_when_event_deleted(self):
        """
        Ensure TicketType is deleted when its related Event is deleted (on_delete=CASCADE).
        """
        ticket = TicketType.objects.create(
            event=self.event,
            name='Early Bird',
            price=50.00,
            quantity_available=20
        )
        self.event.delete()
        self.assertFalse(TicketType.objects.filter(id=ticket.id).exists())
