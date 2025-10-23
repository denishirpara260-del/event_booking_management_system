from django.test import TestCase
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from events.models import Event, TicketType, Booking
from events.forms import BookingForm, APIBookingForm


class BookingFormTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="password")
        self.event = Event.objects.create(
            title="Sample Event",
            location="Main Hall",
            date_time=timezone.now(),
            max_capacity=100,
            is_published=True
        )

        self.ticket_vip = TicketType.objects.create(
            event=self.event,
            name="VIP",
            price=100.00,
            quantity_available=10
        )
        self.ticket_standard = TicketType.objects.create(
            event=self.event,
            name="Standard",
            price=50.00,
            quantity_available=5
        )

    def test_booking_form_valid_data(self):
        form_data = {
            "ticket_type": self.ticket_vip.id,
            "quantity": 3
        }
        form = BookingForm(data=form_data, user=self.user, event=self.event)
        self.assertTrue(form.is_valid())

    def test_booking_form_quantity_exceeds_available(self):
        form_data = {
            "ticket_type": self.ticket_standard.id,
            "quantity": 10
        }
        form = BookingForm(data=form_data, user=self.user, event=self.event)
        self.assertFalse(form.is_valid())
        self.assertIn("Only 5 tickets available", str(form.errors))

    def test_booking_form_save_creates_booking(self):
        form_data = {
            "ticket_type": self.ticket_vip.id,
            "quantity": 2
        }
        form = BookingForm(data=form_data, user=self.user, event=self.event)
        self.assertTrue(form.is_valid())
        booking = form.save()
        self.assertEqual(booking.user, self.user)
        self.assertEqual(booking.ticket_type, self.ticket_vip)
        self.assertEqual(booking.quantity, 2)


class APIBookingFormTest(TestCase):

    def setUp(self):
        self.event1 = Event.objects.create(
            title="Event 1",
            location="Hall A",
            date_time=timezone.now(),
            max_capacity=50,
            is_published=True
        )
        self.event2 = Event.objects.create(
            title="Event 2",
            location="Hall B",
            date_time=timezone.now(),
            max_capacity=30,
            is_published=True
        )

        
        self.ticket1 = TicketType.objects.create(
            event=self.event1,
            name="Standard",
            price=50.00,
            quantity_available=20
        )
        self.ticket2 = TicketType.objects.create(
            event=self.event1,
            name="VIP",
            price=100.00,
            quantity_available=5
        )
        self.ticket3 = TicketType.objects.create(
            event=self.event2,
            name="Regular",
            price=40.00,
            quantity_available=10
        )

    def test_apibooking_form_ticket_queryset_filtered_by_event(self):
        form = APIBookingForm(event_id=self.event1.id)
        ticket_ids = list(form.fields['ticket_type'].queryset.values_list('id', flat=True))
        self.assertIn(self.ticket1.id, ticket_ids)
        self.assertIn(self.ticket2.id, ticket_ids)
        self.assertNotIn(self.ticket3.id, ticket_ids)

    def test_apibooking_form_valid_submission(self):
        form_data = {
            "event": self.event1.id,
            "ticket_type": self.ticket1.id,
            "quantity": 3
        }
        form = APIBookingForm(data=form_data, event_id=self.event1.id)
        self.assertTrue(form.is_valid())

    def test_apibooking_form_invalid_quantity(self):
        form_data = {
            "event": self.event1.id,
            "ticket_type": self.ticket2.id,
            "quantity": 10  
        }
        form = APIBookingForm(data=form_data, event_id=self.event1.id)
        self.assertTrue(form.is_valid())
