from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from club_management.models import (
    CustomUser, Række, Configuration, Substitutliste,
    Week, Day, UserSubstitutAssignment
)
import json

class MeldAfbudTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.række = Række.objects.create(name="Test-række")
        self.config = Configuration.objects.create(
            name="Test Configuration",
            welcome_text="Welcome"
        )
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
        
        # Create a Substitutliste with future deadline
        self.test_date = timezone.now()
        self.test_deadline = self.test_date + timezone.timedelta(days=7)  # 1 week from now
        self.substitutliste = Substitutliste.objects.create(
            name="Test List",
            day=self.test_date,
            deadline=self.test_deadline,
            week=self.week
        )
        
        # Create an assignment
        self.assignment = UserSubstitutAssignment.objects.create(
            user=self.regular_user,
            substitutliste=self.substitutliste,
            status='Ledig'
        )

    def test_meld_afbud_success(self):
        """Test successfully marking an assignment as unavailable."""
        response = self.client.post(
            reverse('meld_afbud'),
            {'assignment_id': self.assignment.id},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['success'])
        
        # Verify status was updated
        self.assignment.refresh_from_db()
        self.assertEqual(self.assignment.status, 'Optaget')

    def test_meld_afbud_invalid_assignment(self):
        """Test marking a non-existent assignment."""
        response = self.client.post(
            reverse('meld_afbud'),
            {'assignment_id': 999},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 404)
        self.assertFalse(response.json()['success'])

    def test_meld_afbud_non_ajax(self):
        """Test marking without AJAX."""
        response = self.client.post(
            reverse('meld_afbud'),
            {'assignment_id': self.assignment.id}
        )
        self.assertEqual(response.status_code, 400)

    def test_meld_afbud_missing_id(self):
        """Test marking without assignment ID."""
        response = self.client.post(
            reverse('meld_afbud'),
            {},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.json()['success'])

    def test_meld_afbud_already_unavailable(self):
        """Test marking an already unavailable assignment."""
        # Mark as unavailable first
        self.assignment.status = 'Optaget'
        self.assignment.save()
        
        response = self.client.post(
            reverse('meld_afbud'),
            {'assignment_id': self.assignment.id},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.json()['success'])

    def test_meld_afbud_past_deadline(self):
        """Test marking after deadline."""
        # Set deadline to yesterday
        self.substitutliste.deadline = timezone.now() - timezone.timedelta(days=1)
        self.substitutliste.save()
        
        response = self.client.post(
            reverse('meld_afbud'),
            {'assignment_id': self.assignment.id},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.json()['success'])
        self.assertIn('deadline', response.json()['error'].lower())

    def test_meld_afbud_concurrent_updates(self):
        """Test concurrent updates to the same assignment."""
        from django.db import transaction
        
        # Simulate concurrent updates in a transaction
        with transaction.atomic():
            # First update
            response1 = self.client.post(
                reverse('meld_afbud'),
                {'assignment_id': self.assignment.id},
                HTTP_X_REQUESTED_WITH='XMLHttpRequest'
            )
            
            # Second update (should fail as already marked)
            response2 = self.client.post(
                reverse('meld_afbud'),
                {'assignment_id': self.assignment.id},
                HTTP_X_REQUESTED_WITH='XMLHttpRequest'
            )
        
        # First update should succeed
        self.assertTrue(response1.json()['success'])
        
        # Second update should fail
        self.assertFalse(response2.json()['success'])
        self.assertEqual(response2.status_code, 400)
        self.assertIn('already', response2.json()['error'].lower())
        
        # Verify final state
        self.assignment.refresh_from_db()
        self.assertEqual(self.assignment.status, 'Optaget') 