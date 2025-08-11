from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.models import User
from club_management.models import (
    Configuration, CustomUser, Række,
    Afmeldingsliste, Substitutliste, Day,
    Week, DayResponsibility, UserSubstitutAssignment
)
import json

class AjaxEndpointTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.config = Configuration.objects.create(
            name="Test Configuration",
            welcome_text="Welcome to test site"
        )
        self.række = Række.objects.create(name="A-række")
        self.week = Week.objects.create(name="1-2024")
        self.day = Day.objects.create(name="Monday")
        
        # Create users
        self.regular_user = CustomUser.objects.create_user(
            username="regular",
            email="regular@test.com",
            password="regular123",
            række=self.række,
            user_type="Substitutter",
            phone_number="+45 12345678"
        )
        
        self.admin_user = CustomUser.objects.create_superuser(
            username="admin",
            email="admin@test.com",
            password="admin123",
            user_type="Substitutter",
            phone_number="+45 87654321"
        )
        
        # Create test data
        self.test_date = timezone.now()
        self.afmeldingsliste = Afmeldingsliste.objects.create(
            name="Test Afmeldingsliste",
            day=self.test_date,
            deadline=self.test_date + timezone.timedelta(days=1)
        )
        
        self.substitutliste = Substitutliste.objects.create(
            name="Test List",
            day=self.test_date,
            deadline=self.test_date + timezone.timedelta(days=1),
            week=self.week
        )
        
        self.assignment = UserSubstitutAssignment.objects.create(
            user=self.regular_user,
            substitutliste=self.substitutliste,
            status='Ledig'
        )

    def test_append_afbud_ajax_success(self):
        """Test successful AJAX request to append_afbud."""
        self.client.login(username='admin', password='admin123')
        
        response = self.client.post(
            reverse('append_afbud', args=[self.afmeldingsliste.id]),
            {'name': 'John Doe'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertEqual(data['message'], 'Afbud added successfully')
        
        # Verify name was added
        self.afmeldingsliste.refresh_from_db()
        self.assertIn('John Doe', self.afmeldingsliste.names)

    def test_append_afbud_non_ajax(self):
        """Test non-AJAX request to append_afbud."""
        self.client.login(username='admin', password='admin123')
        
        response = self.client.post(
            reverse('append_afbud', args=[self.afmeldingsliste.id]),
            {'name': 'John Doe'}
        )
        
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content.decode(), 'Only AJAX requests are allowed')

    def test_append_afbud_past_deadline(self):
        """Test append_afbud after deadline."""
        self.client.login(username='admin', password='admin123')
        
        # Set deadline to past
        self.afmeldingsliste.deadline = timezone.now() - timezone.timedelta(days=1)
        self.afmeldingsliste.save()
        
        response = self.client.post(
            reverse('append_afbud', args=[self.afmeldingsliste.id]),
            {'name': 'John Doe'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertFalse(data['success'])
        self.assertEqual(data['error'], 'Deadline er overskredet')

    def test_select_substitut_ajax_success(self):
        """Test successful AJAX request to select_substitut."""
        response = self.client.post(
            reverse('select_substitut'),
            {
                'assignment_id': self.assignment.id,
                'action': 'reserve',
                'note': 'Test reservation'
            },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertEqual(data['message'], 'Assignment reserved successfully')
        
        # Verify assignment was updated
        self.assignment.refresh_from_db()
        self.assertEqual(self.assignment.status, 'Optaget')
        self.assertEqual(self.assignment.reservationsnote, 'Test reservation')

    def test_select_substitut_invalid_action(self):
        """Test select_substitut with invalid action."""
        response = self.client.post(
            reverse('select_substitut'),
            {
                'assignment_id': self.assignment.id,
                'action': 'invalid_action',
                'note': 'Test reservation'
            },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertFalse(data['success'])
        self.assertEqual(data['error'], 'Invalid action')

    def test_meld_afbud_ajax_success(self):
        """Test successful AJAX request to meld_afbud."""
        response = self.client.post(
            reverse('meld_afbud'),
            {'assignment_id': self.assignment.id},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertEqual(data['message'], 'Assignment marked as unavailable')
        
        # Verify assignment was updated
        self.assignment.refresh_from_db()
        self.assertEqual(self.assignment.status, 'Optaget')

    def test_meld_afbud_non_ajax(self):
        """Test non-AJAX request to meld_afbud."""
        response = self.client.post(
            reverse('meld_afbud'),
            {'assignment_id': self.assignment.id}
        )
        
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content.decode(), 'Only AJAX requests are allowed')

    def test_meld_afbud_already_unavailable(self):
        """Test meld_afbud for already unavailable assignment."""
        # Set assignment as unavailable
        self.assignment.status = 'Optaget'
        self.assignment.save()
        
        response = self.client.post(
            reverse('meld_afbud'),
            {'assignment_id': self.assignment.id},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertFalse(data['success'])
        self.assertEqual(data['error'], 'Assignment is already marked as unavailable')

    def test_meld_afbud_past_deadline(self):
        """Test meld_afbud after deadline."""
        # Set deadline to past
        self.substitutliste.deadline = timezone.now() - timezone.timedelta(days=1)
        self.substitutliste.save()
        
        response = self.client.post(
            reverse('meld_afbud'),
            {'assignment_id': self.assignment.id},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertFalse(data['success'])
        self.assertEqual(data['error'], 'Deadline er overskredet')

    def test_meld_afbud_invalid_assignment(self):
        """Test meld_afbud with invalid assignment ID."""
        response = self.client.post(
            reverse('meld_afbud'),
            {'assignment_id': 999},  # Non-existent ID
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.content)
        self.assertFalse(data['success'])
        self.assertEqual(data['error'], 'Assignment not found') 