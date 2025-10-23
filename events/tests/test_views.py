from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from events.models import Event, TicketType, Booking
from datetime import timedelta

class EventViewsTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="password")
        self.event1 = Event.objects.create(
            title="Event 1",
            location="Hall A",
            date_time=timezone.now() + timedelta(minutes=1),  # future event
            max_capacity=50,
            is_published=True
        )
        self.event2 = Event.objects.create(
            title="Event 2",
            location="Hall B",
            date_time=timezone.now() + timedelta(minutes=1),
            max_capacity=30,
            is_published=True
        )
        self.ticket1 = TicketType.objects.create(
            event=self.event1,
            name="Standard",
            price=50.0,
            quantity_available=20
        )

    def test_upcoming_events_view(self):
        url = reverse('upcoming_events')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.event1.title)
        self.assertContains(response, self.event2.title)

    def test_event_list_view(self):
        url = reverse('event_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.event1.title)
        self.assertContains(response, self.event2.title)

    def test_event_detail_view_requires_login(self):
        url = reverse('event_detail', args=[self.event1.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_event_detail_view_booking(self):
        self.client.login(username="testuser", password="password")
        url = reverse('event_detail', args=[self.event1.id])
        form_data = {"ticket_type": self.ticket1.id, "quantity": 2}
        response = self.client.post(url, data=form_data)
        self.assertEqual(response.status_code, 302)  # Redirect after success
        booking = Booking.objects.filter(user=self.user, ticket_type=self.ticket1).first()
        self.assertIsNotNone(booking)
        self.assertEqual(booking.quantity, 2)


class EventAPITest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username="apiuser", password="password")
        self.token = Token.objects.create(user=self.user)
        self.api_client = APIClient()
        self.api_client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

        self.event = Event.objects.create(
            title="API Event",
            location="API Hall",
            date_time=timezone.now(),
            max_capacity=50,
            is_published=True
        )
        self.ticket = TicketType.objects.create(
            event=self.event,
            name="VIP",
            price=100.0,
            quantity_available=5
        )

    def test_event_list_api(self):
        url = reverse('api_event_list')
        client = APIClient()
        response = client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.event.title)

    def test_ticket_booking_api_success(self):
        url = reverse('api_ticket_booking', args=[self.event.id])
        data = {"ticket_type_id": self.ticket.id, "quantity": 2}
        response = self.api_client.post(url, data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertIn('Booking successful', response.data['message'])

    def test_ticket_booking_api_exceeds_quantity(self):
        url = reverse('api_ticket_booking', args=[self.event.id])
        data = {"ticket_type_id": self.ticket.id, "quantity": 10}
        response = self.api_client.post(url, data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('Not enough tickets available', str(response.data))


class APIBookingFormViewTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username="formuser", password="password")
        self.client.login(username="formuser", password="password")
        self.event = Event.objects.create(
            title="Form Event",
            location="Form Hall",
            date_time=timezone.now(),
            max_capacity=50,
            is_published=True
        )
        self.ticket = TicketType.objects.create(
            event=self.event,
            name="Regular",
            price=50.0,
            quantity_available=10
        )

    def test_api_booking_form_view_get(self):
        url = reverse('api_booking_form')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Select Event")

  
