from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from club_management.models import CustomUser, Række, Configuration
from django.utils import timezone
from django.core.exceptions import ValidationError

class AuthenticationTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.række = Række.objects.create(name="Test-række")
        self.config = Configuration.objects.create(
            name="Test Configuration",
            welcome_text="Welcome"
        )
        
        User = get_user_model()
        # Create regular auth user
        self.regular_user = User.objects.create_user(
            username="regular",
            email="regular@test.com",
            password="regular123",
        )
        # Create superuser
        self.admin_user = User.objects.create_superuser(
            username="admin",
            email="admin@test.com",
            password="admin123",
        )

    def test_login_required_views(self):
        """Test that certain views require login."""
        # Try accessing admin area without login
        response = self.client.get(reverse('admin:index'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
        self.assertTrue(response.url.startswith('/admin/login/'))

    def test_admin_login(self):
        """Test admin login and access."""
        # Login as admin
        logged_in = self.client.login(username="admin", password="admin123")
        self.assertTrue(logged_in)
        
        # Access admin area
        response = self.client.get(reverse('admin:index'))
        self.assertEqual(response.status_code, 200)

    def test_regular_user_admin_access(self):
        """Test that regular users cannot access admin area."""
        # Login as regular user
        logged_in = self.client.login(username="regular", password="regular123")
        self.assertTrue(logged_in)
        
        # Try accessing admin area
        response = self.client.get(reverse('admin:index'))
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_public_views_no_login(self):
        """Test that public views are accessible without login."""
        # Test front page
        response = self.client.get(reverse('front_page'))
        self.assertEqual(response.status_code, 200)
        
        # Test substitutlister
        response = self.client.get(reverse('substitutlister'))
        self.assertEqual(response.status_code, 200)
        
        # Test afmeldingslister
        response = self.client.get(reverse('afmeldingslister'))
        self.assertEqual(response.status_code, 200)

    def test_user_type_validation(self):
        """Test that users must have valid user types."""
        with self.assertRaises(ValidationError):
            user = CustomUser(
                username="invalid",
                email="invalid@test.com",
                password="test123",
                user_type="InvalidType",
                phone_number="+45 12345678"
            )
            user.full_clean()  # Changed from create_user to full_clean for validation

    def test_user_permissions(self):
        """Test user permissions and groups."""
        # Regular user should not have admin permissions
        self.assertFalse(self.regular_user.is_staff)
        self.assertFalse(self.regular_user.is_superuser)
        
        # Admin user should have admin permissions
        self.assertTrue(self.admin_user.is_staff)
        self.assertTrue(self.admin_user.is_superuser)

    def test_password_change(self):
        """Test password change functionality."""
        # Login as regular user
        logged_in = self.client.login(username="regular", password="regular123")
        self.assertTrue(logged_in)
        
        # Change password
        self.regular_user.set_password("newpassword123")
        self.regular_user.save()
        
        # Old password should not work
        self.client.logout()
        logged_in = self.client.login(username="regular", password="regular123")
        self.assertFalse(logged_in)
        
        # New password should work
        logged_in = self.client.login(username="regular", password="newpassword123")
        self.assertTrue(logged_in) 