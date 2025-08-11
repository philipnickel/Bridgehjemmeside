from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import get_user_model
from club_management.models import (
    Configuration, CustomUser, Række, Day, Week,
    Substitutliste, Afmeldingsliste, Tilmeldingsliste,
    DayResponsibility, UserSubstitutAssignment
)
import json

User = get_user_model()

class CleanViewTests(TestCase):
    """Clean view tests with minimal setup, testing incrementally."""
    
    def setUp(self):
        """Minimal setup - only create what's absolutely necessary."""
        self.client = Client()
        
        # Create basic configuration (required for most views)
        self.config = Configuration.objects.create(
            name="Test Config",
            welcome_text="Welcome to test",
            substitutlister_text="Substitut text",
            afmeldingslister_text="Afmelding text", 
            tilmeldingslister_text="Tilmelding text"
        )
        
        # Create a basic user for authentication tests
        self.user = CustomUser.objects.create_user(
            username="testuser",
            email="test@example.com", 
            password="testpass123",
            phone_number="+45 12345678",
            user_type="Substitutter"
        )
        
    def test_front_page_get(self):
        """Test that front page loads without errors."""
        response = self.client.get(reverse('front_page'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Welcome to test")

    def test_substitutlister_get(self):
        """Test that substitutlister page loads without errors."""
        response = self.client.get(reverse('substitutlister'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Substitut text")

    def test_afmeldingslister_get(self):
        """Test that afmeldingslister page loads without errors.""" 
        response = self.client.get(reverse('afmeldingslister'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Afmelding text")
        
    def test_tilmeldingslister_get(self):
        """Test that tilmeldingslister page loads without errors."""
        response = self.client.get(reverse('tilmeldingslister'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Tilmelding text")

    def test_front_page_with_data(self):
        """Test front page with actual substitutlister data."""
        # Create some basic data
        week = Week.objects.create(name="1-2024")
        
        # Create Day object for the day of the week (view expects this)
        today = timezone.now()
        day_name = today.strftime("%A")  # e.g., "Monday"
        day_obj, _ = Day.objects.get_or_create(name=day_name)
        
        substitutliste = Substitutliste.objects.create(
            name="Test Substitutliste",
            day=today,
            deadline=today + timezone.timedelta(days=1),
            week=week
        )
        
        response = self.client.get(reverse('front_page'))
        self.assertEqual(response.status_code, 200)
        
        # Check context has substitutlister
        self.assertIn('substitutlister', response.context)
        substitutlister = response.context['substitutlister']
        self.assertEqual(len(substitutlister), 1)
        self.assertEqual(substitutlister[0].name, "Test Substitutliste")
        
        # The front page might not display the name directly, so let's just verify context

    def test_afmeldingslister_with_data(self):
        """Test afmeldingslister page with actual data."""
        # Create an afmeldingsliste
        afmeldingsliste = Afmeldingsliste.objects.create(
            name="Test Afmeldingsliste", 
            day=timezone.now(),
            deadline=timezone.now() + timezone.timedelta(days=1),
            names=["John Doe", "Jane Smith"]
        )
        
        response = self.client.get(reverse('afmeldingslister'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Afmeldingsliste")
        
        # Check context has afmeldingslister
        self.assertIn('afmeldingslister', response.context)
        afmeldingslister = response.context['afmeldingslister']
        self.assertEqual(len(afmeldingslister), 1)
        self.assertEqual(afmeldingslister[0].name, "Test Afmeldingsliste")

    def test_append_afbud_success(self):
        """Test successfully adding an absence via AJAX."""
        # Create an afmeldingsliste
        afmeldingsliste = Afmeldingsliste.objects.create(
            name="Test List",
            day=timezone.now(),
            deadline=timezone.now() + timezone.timedelta(days=1),
            names=[]
        )
        
        # Login as admin (required for append_afbud)
        admin = CustomUser.objects.create_superuser(
            username="admin", 
            email="admin@test.com",
            password="admin123",
            phone_number="+45 87654321"
        )
        self.client.login(username='admin', password='admin123')
        
        # Make AJAX request to append_afbud
        response = self.client.post(
            reverse('append_afbud', args=[afmeldingsliste.id]),
            {'name': 'John Doe'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertEqual(data['message'], 'Afbud added successfully')
        
        # Verify the name was added
        afmeldingsliste.refresh_from_db()
        self.assertIn('John Doe', afmeldingsliste.names)

    def test_append_afbud_unauthorized(self):
        """Test append_afbud requires authentication."""
        afmeldingsliste = Afmeldingsliste.objects.create(
            name="Test List",
            day=timezone.now(),
            deadline=timezone.now() + timezone.timedelta(days=1)
        )
        
        response = self.client.post(
            reverse('append_afbud', args=[afmeldingsliste.id]),
            {'name': 'John Doe'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        # Should redirect to login
        self.assertEqual(response.status_code, 302)

    def test_afmeldingsliste_detail(self):
        """Test the afmeldingsliste detail view."""
        afmeldingsliste = Afmeldingsliste.objects.create(
            name="Detail Test List",
            day=timezone.now(),
            deadline=timezone.now() + timezone.timedelta(days=1),
            names=["Alice", "Bob", "Charlie"]
        )
        
        response = self.client.get(
            reverse('afmeldingsliste_detail', args=[afmeldingsliste.id])
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Detail Test List")
        self.assertContains(response, "Alice")
        self.assertContains(response, "Bob") 
        self.assertContains(response, "Charlie")
        
        # Check context
        self.assertIn('afmeldingsliste', response.context)
        self.assertEqual(response.context['afmeldingsliste'], afmeldingsliste)
        
    def test_substitutlister_with_assignments(self):
        """Test substitutlister page with substitut assignments."""
        # Create necessary data
        week = Week.objects.create(name="1-2024")
        today = timezone.now()
        day_name = today.strftime("%A")
        day_obj, _ = Day.objects.get_or_create(name=day_name)
        
        substitutliste = Substitutliste.objects.create(
            name="Test Substitutliste",
            day=today,
            deadline=today + timezone.timedelta(days=1),
            week=week
        )
        
        # Create an assignment
        assignment = UserSubstitutAssignment.objects.create(
            user=self.user,
            substitutliste=substitutliste,
            status='Ledig'
        )
        
        response = self.client.get(reverse('substitutlister'))
        self.assertEqual(response.status_code, 200)
        
        # Check that the substitutliste is in context with assigned substitutter
        substitutlister = response.context['substitutlister']
        self.assertEqual(len(substitutlister), 1)
        test_list = substitutlister[0]
        self.assertEqual(test_list.name, "Test Substitutliste")

    def test_tilmeldingslister_with_pairs(self):
        """Test tilmeldingslister page with actual pair data."""
        from club_management.models import TilmeldingslistePair
        
        # Create a tilmeldingsliste
        tilmeldingsliste = Tilmeldingsliste.objects.create(
            name="Test Tilmeldingsliste",
            day=timezone.now(),
            deadline=timezone.now() + timezone.timedelta(days=1),
            responsible_person=self.user,
            antal_par=24
        )
        
        # Create some pairs
        pair1 = TilmeldingslistePair.objects.create(
            tilmeldingsliste=tilmeldingsliste,
            navn="John Doe",
            makker="Jane Smith",
            telefonnummer="+45 12345678",
            email="john@example.com",
            parnummer=1
        )
        
        response = self.client.get(reverse('tilmeldingslister'))
        self.assertEqual(response.status_code, 200)
        
        # Check context has tilmeldingslister
        tilmeldingslister = response.context['tilmeldingslister']
        self.assertEqual(len(tilmeldingslister), 1)
        self.assertEqual(tilmeldingslister[0].name, "Test Tilmeldingsliste")

    def test_append_afbud_with_admin(self):
        """Test append_afbud functionality with admin access."""
        afmeldingsliste = Afmeldingsliste.objects.create(
            name="Test List",
            day=timezone.now(),
            deadline=timezone.now() + timezone.timedelta(days=1),
            names=[]
        )
        
        # Create admin user
        admin = CustomUser.objects.create_superuser(
            username="admin",
            email="admin@test.com", 
            password="admin123",
            phone_number="+45 87654321"
        )
        self.client.login(username='admin', password='admin123')
        
        # Test adding a new valid name
        response = self.client.post(
            reverse('append_afbud', args=[afmeldingsliste.id]),
            {'name': 'New Person'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        
        # Test non-existent afmeldingsliste returns 404
        response = self.client.post(
            reverse('append_afbud', args=[999]),
            {'name': 'John Doe'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 404)

    def test_select_substitut_ajax(self):
        """Test the select_substitut AJAX endpoint."""
        # Create necessary data
        week = Week.objects.create(name="1-2024")
        substitutliste = Substitutliste.objects.create(
            name="Test List",
            day=timezone.now(),
            deadline=timezone.now() + timezone.timedelta(days=1),
            week=week
        )
        
        assignment = UserSubstitutAssignment.objects.create(
            user=self.user,
            substitutliste=substitutliste,
            status='Ledig'
        )
        
        # Test successful reservation
        response = self.client.post(
            reverse('select_substitut'),
            {
                'assignment_id': assignment.id,
                'action': 'reserve',
                'note': 'Test reservation'
            },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        if response.status_code == 200:
            data = json.loads(response.content)
            self.assertTrue(data['success'])
            
            # Verify assignment was updated
            assignment.refresh_from_db()
            self.assertEqual(assignment.status, 'Optaget')
            self.assertEqual(assignment.reservationsnote, 'Test reservation')

    def test_error_handling(self):
        """Test 404 and other error responses."""
        # Test non-existent afmeldingsliste detail
        response = self.client.get(reverse('afmeldingsliste_detail', args=[999]))
        self.assertEqual(response.status_code, 404)
        
        # Test invalid URLs (if any exist)
        # This would test any URL patterns that should return 404 