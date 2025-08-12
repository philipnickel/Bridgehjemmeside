from django.test import TestCase
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from datetime import timedelta
from django.contrib.auth import get_user_model
from club_management.models import (
    Configuration, Week, Day, CustomUser, Række,
    Substitutliste, Afmeldingsliste, Tilmeldingsliste,
    UnavailableDay, DayResponsibility, UserSubstitutAssignment,
    Pair, TilmeldingslistePair
)

class ModelTests(TestCase):
    def setUp(self):
        self.config = Configuration.objects.create(
            name="Test Configuration",
            welcome_text="Welcome to test site"
        )
        self.week = Week.objects.create(name="1-2024")
        self.day = Day.objects.create(name="Monday")
        self.række = Række.objects.create(name="A-række")
        self.user = CustomUser.objects.create_user(
            username="testuser",
            email="test@test.com",
            password="testpass123",
            phone_number="+45 12345678",
            række=self.række
        )
        self.AuthUser = get_user_model()

    def test_configuration_str(self):
        """Test the string representation of Configuration."""
        self.assertEqual(str(self.config), "Velkomsttekst")

    def test_week_str(self):
        """Test the string representation of Week."""
        self.assertEqual(str(self.week), "1-2024")

    def test_substitutliste_creation(self):
        """Test creating a Substitutliste."""
        test_date = timezone.now()
        substitutliste = Substitutliste.objects.create(
            name="Test List",
            day=test_date,
            deadline=test_date,
            week=self.week
        )
        self.assertIsNotNone(substitutliste.id)
        self.assertTrue(str(substitutliste).startswith("Test List"))
        self.assertIn(str(test_date), str(substitutliste))

    def test_afmeldingsliste_creation(self):
        """Test creating an Afmeldingsliste."""
        test_date = timezone.now()
        afmeldingsliste = Afmeldingsliste.objects.create(
            name="Test Afmeldingsliste",
            day=test_date,
            deadline=test_date
        )
        self.assertIsNotNone(afmeldingsliste.id)
        self.assertTrue(str(afmeldingsliste).startswith("Test Afmeldingsliste"))
        self.assertIn(str(test_date), str(afmeldingsliste))

    def test_customuser_creation(self):
        """Test creating a CustomUser with all fields."""
        user = CustomUser.objects.create_user(
            username="newuser",
            email="new@test.com",
            password="newpass123",
            user_type="Substitutter",
            phone_number="+45 12345678",
            række=self.række,
            custom_note="Test note"
        )
        self.assertEqual(user.username, "newuser")
        self.assertEqual(user.email, "new@test.com")
        self.assertEqual(user.user_type, "Substitutter")
        self.assertEqual(user.phone_number, "+45 12345678")
        self.assertEqual(user.række, self.række)
        self.assertEqual(user.custom_note, "Test note")
        self.assertTrue(user.check_password("newpass123"))

    def test_customuser_day_availability(self):
        """Test user day availability management."""
        monday, _ = Day.objects.get_or_create(name="Monday")
        tuesday, _ = Day.objects.get_or_create(name="Tuesday")
        
        # Add available days
        self.user.days_available.add(monday, tuesday)
        self.assertEqual(self.user.days_available.count(), 2)
        self.assertIn(monday, self.user.days_available.all())
        self.assertIn(tuesday, self.user.days_available.all())
        
        # Remove a day
        self.user.days_available.remove(tuesday)
        self.assertEqual(self.user.days_available.count(), 1)
        self.assertIn(monday, self.user.days_available.all())
        self.assertNotIn(tuesday, self.user.days_available.all())

    def test_customuser_day_responsibility(self):
        """Test user day responsibility assignment."""
        # Create test data
        monday, _ = Day.objects.get_or_create(name="Monday")
        coordinator = self.AuthUser.objects.create_user(
            username="coordinator2",
            email="coord2@test.com",
            password="pass123",
            first_name="John",
            last_name="Coordinator"
        )
        
        # Create responsibility
        responsibility = DayResponsibility.objects.create(
            day=monday,
            coordinator=coordinator
        )
        
        # Test relationship  
        self.assertEqual(responsibility.coordinator, coordinator)
        self.assertEqual(responsibility.day, monday)

    def test_customuser_validation(self):
        """Test CustomUser field validation."""
        # Test invalid phone number
        with self.assertRaises(ValidationError):
            user = CustomUser(
                username="badphone",
                phone_number="not a phone number",
                user_type="Substitutter"
            )
            user.full_clean()
        
        # Test invalid email
        with self.assertRaises(ValidationError):
            user = CustomUser(
                username="bademail",
                email="not an email",
                user_type="Substitutter",
                phone_number="+45 12345678"
            )
            user.full_clean()
        
        # Test invalid user type
        with self.assertRaises(ValidationError):
            user = CustomUser(
                username="badtype",
                user_type="InvalidType",
                phone_number="+45 12345678"
            )
            user.full_clean() 

    def test_række_creation_and_str(self):
        """Test creating a Række and its string representation."""
        række = Række.objects.create(name="B-række")
        self.assertEqual(str(række), "B-række")
        self.assertEqual(række.name, "B-række")

    def test_række_validation(self):
        """Test Række field validation."""
        # Test empty name
        with self.assertRaises(ValidationError):
            række = Række(name="")
            række.full_clean()
        
        # Test too long name
        with self.assertRaises(ValidationError):
            række = Række(name="x" * 101)  # Max length is 100
            række.full_clean()

    def test_række_unique_name(self):
        """Test that Række names can be duplicated (no unique constraint in model)."""
        række1 = Række.objects.create(name="Test-række")
        række2 = Række.objects.create(name="Test-række")  # Should work since no unique constraint
        self.assertEqual(række1.name, række2.name)
        self.assertNotEqual(række1.id, række2.id)

    def test_række_with_users(self):
        """Test Række relationship with users."""
        række = Række.objects.create(name="Test-række")
        user1 = CustomUser.objects.create_user(
            username="user1",
            email="user1@test.com",
            password="pass123",
            phone_number="+45 11111111",
            række=række
        )
        user2 = CustomUser.objects.create_user(
            username="user2",
            email="user2@test.com",
            password="pass123",
            phone_number="+45 22222222",
            række=række
        )
        
        # Test reverse relationship
        self.assertEqual(række.customuser_set.count(), 2)
        self.assertIn(user1, række.customuser_set.all())
        self.assertIn(user2, række.customuser_set.all())

    def test_unavailableday_creation(self):
        """Test creating an UnavailableDay."""
        date = timezone.now().date()
        unavailable = UnavailableDay.objects.create(date=date)
        self.assertEqual(str(unavailable), date.strftime("%Y-%m-%d"))
        self.assertEqual(unavailable.date, date)

    def test_unavailableday_validation(self):
        """Test UnavailableDay validation."""
        # Test missing date
        with self.assertRaises(ValidationError):
            day = UnavailableDay()
            day.full_clean()
        
        # Test invalid date format
        with self.assertRaises(ValidationError):
            day = UnavailableDay(date="not a date")
            day.full_clean()

    def test_unavailableday_unique_date(self):
        """Test that UnavailableDay dates can be duplicated (no unique constraint in model)."""
        date = timezone.now().date()
        day1 = UnavailableDay.objects.create(date=date)
        day2 = UnavailableDay.objects.create(date=date)  # Should work since no unique constraint
        self.assertEqual(day1.date, day2.date)
        self.assertNotEqual(day1.id, day2.id)

    def test_usersubstitutassignment_creation(self):
        """Test creating a UserSubstitutAssignment."""
        test_date = timezone.now()
        substitutliste = Substitutliste.objects.create(
            name="Test List",
            day=test_date,
            deadline=test_date,
            week=self.week
        )
        
        assignment = UserSubstitutAssignment.objects.create(
            user=self.user,
            substitutliste=substitutliste,
            status='Ledig'
        )
        
        self.assertEqual(assignment.user, self.user)
        self.assertEqual(assignment.substitutliste, substitutliste)
        self.assertEqual(assignment.status, 'Ledig')
        self.assertIsNone(assignment.reservationsnote)

    def test_usersubstitutassignment_status_transitions(self):
        """Test UserSubstitutAssignment status transitions."""
        test_date = timezone.now()
        substitutliste = Substitutliste.objects.create(
            name="Test List",
            day=test_date,
            deadline=test_date,
            week=self.week
        )
        
        assignment = UserSubstitutAssignment.objects.create(
            user=self.user,
            substitutliste=substitutliste,
            status='Ledig'
        )
        
        # Test status change to Optaget
        assignment.status = 'Optaget'
        assignment.reservationsnote = "Reserved by John"
        assignment.save()
        self.assertEqual(assignment.status, 'Optaget')
        self.assertEqual(assignment.reservationsnote, "Reserved by John")
        
        # Test status change to Fraværende
        assignment.status = 'Fraværende'
        assignment.save()
        self.assertEqual(assignment.status, 'Fraværende')

    def test_usersubstitutassignment_invalid_status(self):
        """Test that invalid status values are rejected."""
        test_date = timezone.now()
        substitutliste = Substitutliste.objects.create(
            name="Test List",
            day=test_date,
            deadline=test_date,
            week=self.week
        )
        
        with self.assertRaises(ValidationError):
            assignment = UserSubstitutAssignment(
                user=self.user,
                substitutliste=substitutliste,
                status='InvalidStatus'
            )
            assignment.full_clean()

    def test_usersubstitutassignment_cascade_delete(self):
        """Test that assignments are deleted when substitutliste is deleted."""
        test_date = timezone.now()
        substitutliste = Substitutliste.objects.create(
            name="Test List",
            day=test_date,
            deadline=test_date,
            week=self.week
        )
        
        assignment = UserSubstitutAssignment.objects.create(
            user=self.user,
            substitutliste=substitutliste,
            status='Ledig'
        )
        
        # Test cascade delete when substitutliste is deleted
        assignment_id = assignment.id
        substitutliste.delete()
        self.assertEqual(UserSubstitutAssignment.objects.filter(id=assignment_id).count(), 0) 

    def test_pair_creation(self):
        """Test creating a Pair."""
        pair = Pair.objects.create(
            navn="John Doe",
            makker="Jane Smith",
            contact_info="+45 12345678"
        )
        
        self.assertEqual(pair.navn, "John Doe")
        self.assertEqual(pair.makker, "Jane Smith")
        self.assertEqual(pair.contact_info, "+45 12345678")
        self.assertEqual(str(pair), "John Doe & Jane Smith")

    def test_pair_without_makker(self):
        """Test creating a Pair without a makker."""
        pair = Pair.objects.create(
            navn="John Doe",
            contact_info="+45 12345678"
        )
        
        self.assertEqual(pair.navn, "John Doe")
        self.assertIsNone(pair.makker)
        self.assertEqual(str(pair), "John Doe & Ingen Makker")

    def test_pair_validation(self):
        """Test Pair field validation."""
        # Test pair without navn (should work since default="Unknown")
        pair = Pair(
            contact_info="+45 12345678"
        )
        pair.full_clean()  # Should not raise ValidationError because navn has default
        self.assertEqual(pair.navn, "Unknown")  # Should use default value
        
        # Test valid pair
        pair = Pair(
            navn="John Doe",
            makker="Jane Smith",
            contact_info="+45 12345678"
        )
        pair.full_clean()  # Should not raise ValidationError

    def test_tilmeldingsliste_pair_creation(self):
        """Test creating a TilmeldingslistePair."""
        test_date = timezone.now()
        # Create a regular User for responsible_person
        regular_user = self.AuthUser.objects.create_user(
            username="coordinator",
            email="coord@test.com",
            password="pass123"
        )
        tilmeldingsliste = Tilmeldingsliste.objects.create(
            name="Test List",
            day=test_date,
            deadline=test_date + timezone.timedelta(days=1),
            responsible_person=regular_user,
            antal_par=24
        )
        
        # Create a regular pair
        pair = TilmeldingslistePair.objects.create(
            tilmeldingsliste=tilmeldingsliste,
            navn="John Doe",
            makker="Jane Smith",
            telefonnummer="+45 12345678",
            email="john@example.com"
        )
        
        self.assertEqual(pair.navn, "John Doe")
        self.assertEqual(pair.makker, "Jane Smith")
        self.assertEqual(pair.telefonnummer, "+45 12345678")
        self.assertEqual(pair.email, "john@example.com")
        self.assertFalse(pair.is_single)
        self.assertEqual(str(pair), "John Doe & Jane Smith")

    def test_tilmeldingsliste_pair_single_player(self):
        """Test creating a TilmeldingslistePair for a single player."""
        test_date = timezone.now()
        # Create a regular User for responsible_person
        regular_user = self.AuthUser.objects.create_user(
            username="coordinator2",
            email="coord2@test.com",
            password="pass123"
        )
        tilmeldingsliste = Tilmeldingsliste.objects.create(
            name="Test List",
            day=test_date,
            deadline=test_date + timezone.timedelta(days=1),
            responsible_person=regular_user,
            antal_par=24
        )
        
        # Create a single player
        pair = TilmeldingslistePair.objects.create(
            tilmeldingsliste=tilmeldingsliste,
            navn="Single Player",
            telefonnummer="+45 12345678",
            email="single@example.com",
            is_single=True
        )
        
        self.assertEqual(pair.navn, "Single Player")
        self.assertIsNone(pair.makker)
        self.assertEqual(pair.telefonnummer, "+45 12345678")
        self.assertEqual(pair.email, "single@example.com")
        self.assertTrue(pair.is_single)
        self.assertEqual(str(pair), "Single Player & Ingen Makker")



    def test_tilmeldingsliste_pair_cascade_delete(self):
        """Test that pairs are deleted when their tilmeldingsliste is deleted."""
        test_date = timezone.now()
        # Create a regular User for responsible_person
        regular_user = self.AuthUser.objects.create_user(
            username="coordinator4",
            email="coord4@test.com",
            password="pass123"
        )
        tilmeldingsliste = Tilmeldingsliste.objects.create(
            name="Test List",
            day=test_date,
            deadline=test_date + timezone.timedelta(days=1),
            responsible_person=regular_user,
            antal_par=24
        )
        
        # Create some pairs
        pair1 = TilmeldingslistePair.objects.create(
            tilmeldingsliste=tilmeldingsliste,
            navn="John Doe",
            makker="Jane Smith",
            parnummer=1
        )
        
        pair2 = TilmeldingslistePair.objects.create(
            tilmeldingsliste=tilmeldingsliste,
            navn="Bob Wilson",
            makker="Alice Brown",
            parnummer=2
        )
        
        # Delete the tilmeldingsliste
        tilmeldingsliste.delete()
        
        # Verify pairs were deleted
        self.assertEqual(TilmeldingslistePair.objects.count(), 0) 