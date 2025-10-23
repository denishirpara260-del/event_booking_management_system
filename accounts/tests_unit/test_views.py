from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from events.models import Event, TicketType, Booking
from django.utils import timezone

class AccountsViewsTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.register_url = reverse('register')
        self.login_url = reverse('login')
        self.logout_url = reverse('logout')
        self.profile_url = reverse('profile')

        self.user = User.objects.create_user(username='testuser', password='password123')
        self.event = Event.objects.create(
            title='Test Event',
            location='Test Hall',
            date_time=timezone.now(),
            max_capacity=50,
            is_published=True
        )
        self.ticket = TicketType.objects.create(
            event=self.event,
            name='VIP',
            price=100.0,
            quantity_available=10
        )
        self.booking = Booking.objects.create(
            user=self.user,
            event=self.event,
            ticket_type=self.ticket,
            quantity=2
        )

    def test_register_view_get(self):
        response = self.client.get(self.register_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'register.html')

    def test_register_view_post_valid(self):
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'ComplexPass123',
            'password2': 'ComplexPass123'
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_register_view_post_invalid(self):
        data = {
            'username': '',
            'email': '',
            'password1': 'pass',
            'password2': 'wrongpass'
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, 200)
        form = response.context['form']
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)
        self.assertIn('email', form.errors)

    def test_login_view_get(self):
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login.html')

    def test_login_view_post_valid(self):
        data = {'username': 'testuser', 'password': 'password123'}
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.endswith(self.profile_url))

    def test_login_view_post_invalid(self):
        data = {'username': 'testuser', 'password': 'wrongpassword'}
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Please enter a correct username and password.")

    def test_logout_view(self):
        self.client.login(username='testuser', password='password123')
        response = self.client.get(self.logout_url)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.endswith(self.login_url))

    def test_profile_view_requires_login(self):
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, 302)

    def test_profile_view_logged_in(self):
        self.client.login(username='testuser', password='password123')
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profile.html')
        self.assertContains(response, self.user.username)
        self.assertContains(response, self.event.title)
