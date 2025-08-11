from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from club_management.models import (
    CustomUser, Række, Configuration, Afmeldingsliste,
    Week, Day
)

class AfmeldingslisteTests(TestCase):
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
        
        # Create an Afmeldingsliste with future deadline
        self.test_date = timezone.now()
        self.test_deadline = self.test_date + timezone.timedelta(days=7)  # 1 week from now
        self.afmeldingsliste = Afmeldingsliste.objects.create(
            name="Test List",
            day=self.test_date,
            deadline=self.test_deadline
        )

    def test_detail_view_loads(self):
        """Test that detail view loads correctly."""
        response = self.client.get(reverse('afmeldingsliste_detail', args=[self.afmeldingsliste.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'afmeldingsliste_detail.html')
        self.assertEqual(response.context['afmeldingsliste'], self.afmeldingsliste)

    def test_detail_view_404(self):
        """Test 404 for non-existent list."""
        response = self.client.get(reverse('afmeldingsliste_detail', args=[999]))
        self.assertEqual(response.status_code, 404)

    def test_detail_view_context(self):
        """Test that context contains required data."""
        # Add some names to the list
        self.afmeldingsliste.names = "Alice\nBob\nCharlie"
        self.afmeldingsliste.save()
        
        response = self.client.get(reverse('afmeldingsliste_detail', args=[self.afmeldingsliste.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['afmeldingsliste'], self.afmeldingsliste)
        self.assertEqual(response.context['names'], ['Alice', 'Bob', 'Charlie'])

    def test_add_name_success(self):
        """Test successfully adding a name."""
        response = self.client.post(
            reverse('append_afbud', args=[self.afmeldingsliste.id]),
            {'name': 'David'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['success'])
        
        # Verify name was added
        self.afmeldingsliste.refresh_from_db()
        self.assertIn('David', self.afmeldingsliste.names.split('\n'))

    def test_add_duplicate_name(self):
        """Test adding a duplicate name."""
        # Add initial name
        self.afmeldingsliste.names = "David"
        self.afmeldingsliste.save()
        
        # Try to add same name again
        response = self.client.post(
            reverse('append_afbud', args=[self.afmeldingsliste.id]),
            {'name': 'David'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json()['success'])
        self.assertIn('already exists', response.json()['error'])

    def test_add_empty_name(self):
        """Test adding an empty name."""
        response = self.client.post(
            reverse('append_afbud', args=[self.afmeldingsliste.id]),
            {'name': ''},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json()['success'])
        self.assertIn('empty', response.json()['error'].lower())

    def test_add_name_non_ajax(self):
        """Test adding name without AJAX."""
        response = self.client.post(
            reverse('append_afbud', args=[self.afmeldingsliste.id]),
            {'name': 'David'}
        )
        self.assertEqual(response.status_code, 400)

    def test_add_name_invalid_list(self):
        """Test adding name to non-existent list."""
        response = self.client.post(
            reverse('append_afbud', args=[999]),
            {'name': 'David'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 404)

    def test_past_deadline(self):
        """Test adding name after deadline."""
        # Set deadline to yesterday
        yesterday = timezone.now() - timezone.timedelta(days=1)
        self.afmeldingsliste.deadline = yesterday
        self.afmeldingsliste.save()
        
        response = self.client.post(
            reverse('append_afbud', args=[self.afmeldingsliste.id]),
            {'name': 'David'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json()['success'])
        self.assertIn('deadline', response.json()['error'].lower())

    def test_name_whitespace_handling(self):
        """Test handling of whitespace in names."""
        # Test with leading/trailing whitespace
        response = self.client.post(
            reverse('append_afbud', args=[self.afmeldingsliste.id]),
            {'name': '  David  '},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['success'])
        
        # Verify whitespace was stripped
        self.afmeldingsliste.refresh_from_db()
        self.assertIn('David', self.afmeldingsliste.names.split('\n'))
        self.assertNotIn('  David  ', self.afmeldingsliste.names.split('\n'))

    def test_concurrent_updates(self):
        """Test concurrent updates to the list."""
        from django.db import transaction
        
        # Add initial names
        self.afmeldingsliste.names = "Alice\nBob"
        self.afmeldingsliste.save()
        
        # Simulate concurrent updates in a transaction
        with transaction.atomic():
            # First update
            response1 = self.client.post(
                reverse('append_afbud', args=[self.afmeldingsliste.id]),
                {'name': 'Charlie'},
                HTTP_X_REQUESTED_WITH='XMLHttpRequest'
            )
            
            # Second update
            response2 = self.client.post(
                reverse('append_afbud', args=[self.afmeldingsliste.id]),
                {'name': 'David'},
                HTTP_X_REQUESTED_WITH='XMLHttpRequest'
            )
        
        # Verify both updates succeeded
        self.assertTrue(response1.json()['success'])
        self.assertTrue(response2.json()['success'])
        
        # Verify final state
        self.afmeldingsliste.refresh_from_db()
        names = self.afmeldingsliste.names.split('\n')
        self.assertIn('Charlie', names)
        self.assertIn('David', names) 