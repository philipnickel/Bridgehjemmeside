from django.test import TestCase
from django.core.exceptions import ValidationError
from club_management.forms import CustomUserForm
from club_management.models import CustomUser, Række, Day

class CustomUserFormTests(TestCase):
    def setUp(self):
        self.række = Række.objects.create(name="Test-række")
        self.monday = Day.objects.create(name="Monday")
        self.tuesday = Day.objects.create(name="Tuesday")
        self.saturday = Day.objects.create(name="Lørdag")
        self.sunday = Day.objects.create(name="Søndag")

    def test_valid_form(self):
        """Test form with valid data."""
        form_data = {
            'username': 'testuser',
            'user_type': 'Substitutter',
            'phone_number': '+45 12345678',
            'email': 'test@example.com',
            'række': self.række.id,
            'days_available': [self.monday.id, self.tuesday.id],
            'custom_note': 'Test note',
            'password1': 'testpass123',
            'password2': 'testpass123'
        }
        form = CustomUserForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_required_fields(self):
        """Test that required fields are enforced."""
        form = CustomUserForm(data={})
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)
        self.assertIn('user_type', form.errors)
        self.assertIn('phone_number', form.errors)

    def test_optional_fields(self):
        """Test that optional fields are truly optional."""
        form_data = {
            'username': 'testuser',
            'user_type': 'Substitutter',
            'phone_number': '+45 12345678',
            'email': 'test@example.com',
            'række': self.række.id,
            'password1': 'testpass123',
            'password2': 'testpass123'
        }
        form = CustomUserForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_invalid_email(self):
        """Test email validation."""
        form_data = {
            'username': 'testuser',
            'user_type': 'Substitutter',
            'phone_number': '+45 12345678',
            'email': 'not-an-email',
            'række': self.række.id
        }
        form = CustomUserForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    def test_phone_number_accepts_various_formats(self):
        """Test that phone number accepts various formats (no strict validation)."""
        form_data = {
            'username': 'testuser',
            'user_type': 'Substitutter',
            'phone_number': 'not-a-phone',  # Should be accepted since no strict validation
            'email': 'test@example.com',
            'række': self.række.id
        }
        form = CustomUserForm(data=form_data)
        self.assertTrue(form.is_valid())  # Phone number validation is not strict

    def test_invalid_user_type(self):
        """Test user type validation."""
        form_data = {
            'username': 'testuser',
            'user_type': 'InvalidType',
            'phone_number': '+45 12345678',
            'email': 'test@example.com',
            'række': self.række.id
        }
        form = CustomUserForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('user_type', form.errors)

    def test_weekend_days_excluded(self):
        """Test that weekend days are excluded from available days."""
        form = CustomUserForm()
        available_days = form.fields['days_available'].queryset
        self.assertNotIn(self.saturday, available_days)
        self.assertNotIn(self.sunday, available_days)
        self.assertIn(self.monday, available_days)
        self.assertIn(self.tuesday, available_days)

    def test_form_save(self):
        """Test that form saves correctly."""
        form_data = {
            'username': 'testuser',
            'user_type': 'Substitutter',
            'phone_number': '+45 12345678',
            'email': 'test@example.com',
            'række': self.række.id,
            'days_available': [self.monday.id, self.tuesday.id],
            'custom_note': 'Test note',
            'password1': 'testpass123',
            'password2': 'testpass123'
        }
        form = CustomUserForm(data=form_data)
        self.assertTrue(form.is_valid())
        
        # Save the form
        user = form.save()
        
        # Verify saved data
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.user_type, 'Substitutter')
        self.assertEqual(user.phone_number, '+45 12345678')
        self.assertEqual(user.email, 'test@example.com')
        self.assertEqual(user.række, self.række)
        self.assertEqual(user.custom_note, 'Test note')
        self.assertEqual(list(user.days_available.all()), [self.monday, self.tuesday])

    def test_unique_username(self):
        """Test that usernames must be unique."""
        # Create first user
        form_data = {
            'username': 'testuser',
            'user_type': 'Substitutter',
            'phone_number': '+45 12345678',
            'email': 'test@example.com',
            'række': self.række.id,
            'password1': 'testpass123',
            'password2': 'testpass123'
        }
        form = CustomUserForm(data=form_data)
        self.assertTrue(form.is_valid())
        form.save()
        
        # Try to create second user with same username
        form = CustomUserForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)

    def test_form_update(self):
        """Test updating an existing user."""
        # Create user
        user = CustomUser.objects.create_user(
            username='testuser',
            user_type='Substitutter',
            phone_number='+45 12345678',
            email='test@example.com',
            password='oldpass123',
            række=self.række
        )
        user.days_available.add(self.monday)
        
        # Update user
        form_data = {
            'username': 'testuser',  # Same username (should be allowed for same user)
            'user_type': 'Substitutter',
            'phone_number': '+45 87654321',  # Changed
            'email': 'new@example.com',  # Changed
            'række': self.række.id,
            'days_available': [self.tuesday.id],  # Changed
            'custom_note': 'Updated note',  # Added
            'password1': 'newpass123',
            'password2': 'newpass123'
        }
        form = CustomUserForm(data=form_data, instance=user)
        self.assertTrue(form.is_valid())
        
        # Save and verify updates
        updated_user = form.save()
        self.assertEqual(updated_user.phone_number, '+45 87654321')
        self.assertEqual(updated_user.email, 'new@example.com')
        self.assertEqual(list(updated_user.days_available.all()), [self.tuesday])
        self.assertEqual(updated_user.custom_note, 'Updated note') 