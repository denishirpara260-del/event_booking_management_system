from django.test import TestCase
from django.contrib.auth.models import User
from accounts.forms import RegisterForm


class RegisterFormTest(TestCase):

    def test_register_form_valid_data(self):
        form_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password1': 'StrongPass123',
            'password2': 'StrongPass123',
        }
        form = RegisterForm(data=form_data)
        self.assertTrue(form.is_valid())
        user = form.save()
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@example.com')

    def test_register_form_password_mismatch(self):
        form_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password1': 'StrongPass123',
            'password2': 'WrongPass123',
        }
        form = RegisterForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)

    def test_register_form_missing_email(self):
        form_data = {
            'username': 'testuser',
            'password1': 'StrongPass123',
            'password2': 'StrongPass123',
        }
        form = RegisterForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    def test_register_form_widget_class(self):
        form = RegisterForm()
        for field_name, field in form.fields.items():
            self.assertIn('form-control', field.widget.attrs.get('class', ''))
