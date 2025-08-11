from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from django.core import mail
from club_management.models import (
    CustomUser, Række, Configuration, Substitutliste,
    Week, Day, UserSubstitutAssignment
)

class NotificationTests(TestCase):
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
            week=self.week,
            responsible_person=self.admin_user  # Set responsible person
        )
        
        # Create an assignment
        self.assignment = UserSubstitutAssignment.objects.create(
            user=self.regular_user,
            substitutliste=self.substitutliste,
            status='Ledig'
        )

    def test_email_on_assignment_update(self):
        """Test that email is sent when assignment is updated."""
        # Clear any existing messages
        mail.outbox = []
        
        # Update assignment
        response = self.client.post(
            reverse('meld_afbud'),
            {'assignment_id': self.assignment.id},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertTrue(response.json()['success'])
        
        # Check that one email was sent
        self.assertEqual(len(mail.outbox), 1)
        
        # Verify email content
        email = mail.outbox[0]
        self.assertEqual(email.subject, 'Substitut har meldt afbud')
        self.assertIn(self.regular_user.username, email.body)
        self.assertIn(self.substitutliste.name, email.body)
        self.assertIn(str(self.substitutliste.day), email.body)

    def test_no_email_on_invalid_assignment(self):
        """Test that no email is sent for invalid assignment."""
        # Clear any existing messages
        mail.outbox = []
        
        # Try to update non-existent assignment
        response = self.client.post(
            reverse('meld_afbud'),
            {'assignment_id': 999},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertFalse(response.json()['success'])
        
        # Check that no email was sent
        self.assertEqual(len(mail.outbox), 0)

    def test_no_email_on_already_unavailable(self):
        """Test that no email is sent when assignment is already unavailable."""
        # Mark as unavailable first
        self.assignment.status = 'Optaget'
        self.assignment.save()
        
        # Clear any existing messages
        mail.outbox = []
        
        # Try to update again
        response = self.client.post(
            reverse('meld_afbud'),
            {'assignment_id': self.assignment.id},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertFalse(response.json()['success'])
        
        # Check that no email was sent
        self.assertEqual(len(mail.outbox), 0)

    def test_no_email_on_past_deadline(self):
        """Test that no email is sent when past deadline."""
        # Set deadline to yesterday
        self.substitutliste.deadline = timezone.now() - timezone.timedelta(days=1)
        self.substitutliste.save()
        
        # Clear any existing messages
        mail.outbox = []
        
        # Try to update
        response = self.client.post(
            reverse('meld_afbud'),
            {'assignment_id': self.assignment.id},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertFalse(response.json()['success'])
        
        # Check that no email was sent
        self.assertEqual(len(mail.outbox), 0)

    def test_email_content_format(self):
        """Test email content format."""
        # Clear any existing messages
        mail.outbox = []
        
        # Update assignment
        response = self.client.post(
            reverse('meld_afbud'),
            {'assignment_id': self.assignment.id},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertTrue(response.json()['success'])
        
        # Check email format
        email = mail.outbox[0]
        self.assertEqual(email.from_email, 'from@example.com')
        self.assertEqual(email.to, [self.admin_user.email])  # Assuming admin is responsible
        self.assertTrue(email.body.strip())  # Not empty
        self.assertTrue(email.subject.strip())  # Not empty 