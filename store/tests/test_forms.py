"""
Tests for form validation: UserRegistrationForm and UserUpdateForm.
Covers: required fields, password matching, field formats, and optional fields.
"""
from django.test import TestCase
from django.core.exceptions import ValidationError
from store.forms import UserRegistrationForm, UserUpdateForm


class UserRegistrationFormTests(TestCase):
    def test_valid_form_data(self):
        form_data = {
            'first_name': 'Alice',
            'last_name': 'Smith',
            'email_address': 'alice@example.com',
            'DOB': '1995-06-15',
            'gender': 'Female',
            'phone_numbers': '555-1234',
            'house': '789 Oak St',
            'street_name': 'Oak Street',
            'town_city': 'Boston',
            'county': 'Suffolk',
            'postcode': '02108',
            'country': 'US',
            'state': 'MA',
            'password1': 'securepass123',
            'password2': 'securepass123',
            'membership': 'Standard'
        }
        form = UserRegistrationForm(data=form_data)
        self.assertTrue(form.is_valid(), f"Form errors: {form.errors}")

    def test_password_mismatch(self):
        form_data = {
            'first_name': 'Bob',
            'last_name': 'Brown',
            'email_address': 'bob@example.com',
            'DOB': '1990-01-01',
            'gender': 'Male',
            'house': '123 Main',
            'street_name': 'Main St',
            'town_city': 'City',
            'county': 'County',
            'postcode': '12345',
            'country': 'US',
            'state': 'CA',
            'password1': 'pass123',
            'password2': 'pass456',
            'membership': 'None'
        }
        form = UserRegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('__all__', form.errors)
        self.assertIn("Passwords do not match", str(form.errors['__all__']))

    def test_missing_required_fields(self):
        form_data = {
            'first_name': '',  # required
            'last_name': 'Doe',
            'email_address': 'doe@example.com',
            'DOB': '1995-05-05',
            'gender': 'Male',
            'house': '456 Elm',
            'street_name': 'Elm St',
            'town_city': 'Town',
            'county': 'County',
            'postcode': '67890',
            'country': 'GB',
            'password1': 'test123',
            'password2': 'test123',
            'membership': 'Premium'
        }
        form = UserRegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('first_name', form.errors)

    def test_invalid_email_format(self):
        form_data = {
            'first_name': 'Test',
            'last_name': 'User',
            'email_address': 'not-an-email',
            'DOB': '1990-01-01',
            'gender': 'Male',
            'house': '1',
            'street_name': 'St',
            'town_city': 'City',
            'county': 'C',
            'postcode': '00000',
            'country': 'US',
            'password1': 'test123',
            'password2': 'test123',
            'membership': 'Student'
        }
        form = UserRegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email_address', form.errors)

    def test_optional_fields_work(self):
        form_data = {
            'first_name': 'Min',
            'last_name': 'Data',
            'email_address': 'minimal@example.com',
            'DOB': '2000-01-01',
            'gender': 'Female',
            'house': '1',
            'street_name': 'One',
            'town_city': 'Place',
            'county': '',
            'postcode': '',
            'country': 'FR',
            'password1': 'pw123',
            'password2': 'pw123',
            'membership': 'None'
        }
        form = UserRegistrationForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_membership_none_not_required(self):
        form_data = {
            'first_name': 'No',
            'last_name': 'Member',
            'email_address': 'nomember@example.com',
            'DOB': '1999-09-09',
            'gender': 'Male',
            'house': '0',
            'street_name': 'Zero',
            'town_city': 'Nowhere',
            'county': 'None',
            'postcode': '00000',
            'country': 'US',
            'password1': 'pw',
            'password2': 'pw',
            'membership': 'None'
        }
        form = UserRegistrationForm(data=form_data)
        self.assertTrue(form.is_valid())


class UserUpdateFormTests(TestCase):
    def test_update_with_all_fields(self):
        form_data = {
            'first_name': 'Updated',
            'last_name': 'Name',
            'email_address': 'updated@example.com',
            'DOB': '1991-02-02',
            'phone_numbers': '555-9999',
            'gender': 'Female',
            'house': '999 New',
            'street_name': 'New Street',
            'town_city': 'New City',
            'county': 'New County',
            'postcode': '98765',
            'country': 'US',
            'state': 'CA',  # Valid US state
            'password': 'newpass123',
            'membership': 'Premium'
        }
        form = UserUpdateForm(data=form_data)
        self.assertTrue(form.is_valid(), f"Errors: {form.errors}")

    def test_update_partial_fields(self):
        form_data = {
            'first_name': 'Partial',
            # Most fields omitted (all optional)
        }
        form = UserUpdateForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_update_with_invalid_email(self):
        form_data = {
            'email_address': 'invalid-email-format',
        }
        form = UserUpdateForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email_address', form.errors)

    def test_update_optional_all_blank(self):
        form_data = {}
        form = UserUpdateForm(data=form_data)
        self.assertTrue(form.is_valid())
