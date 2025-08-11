from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from club_management.models import CustomUser, Række

class LoginViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.række = Række.objects.create(name="Test-række")
        
        # Create regular user
        self.regular_user = CustomUser.objects.create_user(
            username="regular",
            email="regular@test.com",
            password="regular123",
            række=self.række,
            user_type="Substitutter",
            phone_number="+45 12345678"
        )
        
        # Create superuser
        self.admin_user = CustomUser.objects.create_superuser(
            username="admin",
            email="admin@test.com",
            password="admin123",
            user_type="Substitutter",
            phone_number="+45 87654321"
        )

    def test_login_page_loads(self):
        """Test that login page loads correctly."""
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login.html')

    def test_successful_login_regular_user(self):
        """Test successful login for regular user."""
        response = self.client.post(reverse('login'), {
            'username': 'regular',
            'password': 'regular123'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after login
        self.assertTrue(response.url.startswith(reverse('front_page')))
        
        # Verify user is logged in
        response = self.client.get(reverse('front_page'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['user'].is_authenticated)
        self.assertEqual(response.context['user'], self.regular_user)

    def test_successful_login_admin_user(self):
        """Test successful login for admin user."""
        response = self.client.post(reverse('login'), {
            'username': 'admin',
            'password': 'admin123'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after login
        self.assertTrue(response.url.startswith(reverse('admin:index')))
        
        # Verify admin access
        response = self.client.get(reverse('admin:index'))
        self.assertEqual(response.status_code, 200)

    def test_failed_login_wrong_password(self):
        """Test login failure with wrong password."""
        response = self.client.post(reverse('login'), {
            'username': 'regular',
            'password': 'wrongpass'
        })
        self.assertEqual(response.status_code, 200)  # Stay on login page
        self.assertTemplateUsed(response, 'login.html')
        self.assertContains(response, 'Invalid username or password')
        
        # Verify user is not logged in
        response = self.client.get(reverse('admin:index'))
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_failed_login_nonexistent_user(self):
        """Test login failure with nonexistent user."""
        response = self.client.post(reverse('login'), {
            'username': 'nonexistent',
            'password': 'somepass'
        })
        self.assertEqual(response.status_code, 200)  # Stay on login page
        self.assertTemplateUsed(response, 'login.html')
        self.assertContains(response, 'Invalid username or password')

    def test_login_required_redirect(self):
        """Test redirect to login for protected views."""
        # Try accessing admin without login
        response = self.client.get(reverse('admin:index'))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/admin/login/'))
        
        # Login and verify access
        self.client.login(username='admin', password='admin123')
        response = self.client.get(reverse('admin:index'))
        self.assertEqual(response.status_code, 200)

    def test_login_with_next_parameter(self):
        """Test login with next parameter for redirect."""
        target_url = reverse('admin:index')
        login_url = f"{reverse('login')}?next={target_url}"
        
        response = self.client.post(login_url, {
            'username': 'admin',
            'password': 'admin123'
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, target_url)

    def test_already_logged_in_redirect(self):
        """Test that logged-in users are redirected from login page."""
        # Login first
        self.client.login(username='regular', password='regular123')
        
        # Try accessing login page
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(reverse('front_page')))

    def test_csrf_protection(self):
        """Test CSRF protection on login form."""
        # Create a client that doesn't enforce CSRF
        csrf_client = Client(enforce_csrf_checks=True)
        
        response = csrf_client.post(reverse('login'), {
            'username': 'regular',
            'password': 'regular123'
        })
        self.assertEqual(response.status_code, 403)  # CSRF validation failed

    def test_form_validation(self):
        """Test login form validation."""
        # Test empty form
        response = self.client.post(reverse('login'), {})
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'username', 'This field is required.')
        self.assertFormError(response, 'form', 'password', 'This field is required.')
        
        # Test empty password
        response = self.client.post(reverse('login'), {
            'username': 'regular'
        })
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'password', 'This field is required.') 