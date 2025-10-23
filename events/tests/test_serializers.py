from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework.exceptions import ValidationError
from events.models import Event, TicketType, Booking
from events.serializers import EventSerializer, TicketBookingSerializer


class EventSerializerTest(TestCase):

    def setUp(self):
        self.event = Event.objects.create(
            title="Test Event",
            description="Sample description",
            date_time=timezone.now(),
            location="Main Hall",
            max_capacity=100,
            is_published=True
        )

    def test_event_serializer_fields(self):
        serializer = EventSerializer(instance=self.event)
        data = serializer.data
        self.assertEqual(data['id'], self.event.id)
        self.assertEqual(data['title'], "Test Event")
        self.assertEqual(data['description'], "Sample description")
        self.assertEqual(data['location'], "Main Hall")
        self.assertEqual(data['max_capacity'], 100)


class TicketBookingSerializerTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="password")
        self.event = Event.objects.create(
            title="Concert",
            location="Auditorium",
            date_time=timezone.now(),
            max_capacity=50,
            is_published=True
        )
        self.ticket_vip = TicketType.objects.create(
            event=self.event,
            name="VIP",
            price=100.0,
            quantity_available=5
        )
        self.ticket_standard = TicketType.objects.create(
            event=self.event,
            name="Standard",
            price=50.0,
            quantity_available=10
        )

    def test_ticket_booking_serializer_valid(self):
        data = {
            "ticket_type_id": self.ticket_standard.id,
            "quantity": 3
        }
        serializer = TicketBookingSerializer(data=data, context={"request": self._get_mock_request()})
        self.assertTrue(serializer.is_valid(), serializer.errors)
        booking = serializer.save()
        self.assertEqual(booking.user, self.user)
        self.assertEqual(booking.ticket_type, self.ticket_standard)
        self.assertEqual(booking.quantity, 3)

    def test_ticket_booking_serializer_invalid_ticket_type(self):
        data = {
            "ticket_type_id": 9999,  
            "quantity": 1
        }
        serializer = TicketBookingSerializer(data=data, context={"request": self._get_mock_request()})
        with self.assertRaises(ValidationError):
            serializer.is_valid(raise_exception=True)

    def test_ticket_booking_serializer_quantity_exceeds(self):
        data = {
            "ticket_type_id": self.ticket_vip.id,
            "quantity": 10  
        }
        serializer = TicketBookingSerializer(data=data, context={"request": self._get_mock_request()})
        self.assertFalse(serializer.is_valid())
        self.assertIn("Not enough tickets available", str(serializer.errors))

    def _get_mock_request(self):
        """Return a mock request object with self.user"""
        class MockRequest:
            user = self.user
        return MockRequest()
