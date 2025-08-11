from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from club_management.models import (
    Configuration, CustomUser, Række,
    Afmeldingsliste, Substitutliste, Day,
    Week, DayResponsibility, UserSubstitutAssignment,
    Tilmeldingsliste, TilmeldingslistePair
)
import json

class ViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.config = Configuration.objects.create(
            name="Test Configuration",
            welcome_text="Welcome to test site",
            substitutlister_text="Default text",
            afmeldingslister_text="Default text",
            tilmeldingslister_text="Default text"
        )
        self.række = Række.objects.create(name="A-række")
        self.week = Week.objects.create(name="1-2024")
        self.day, _ = Day.objects.get_or_create(name="Monday")
        
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
        
        # Create coordinator
        self.coordinator = CustomUser.objects.create_user(
            username="coordinator",
            email="coord@test.com",
            password="pass123",
            first_name="John",
            last_name="Coordinator",
            user_type="Substitutter",
            phone_number="+45 11111111"
        )
        
        # Create day responsibility
        self.responsibility = DayResponsibility.objects.create(
            day=self.day,
            coordinator=self.coordinator
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
        
        self.tilmeldingsliste = Tilmeldingsliste.objects.create(
            name="Test List",
            day=self.test_date,
            deadline=self.test_date + timezone.timedelta(days=1),
            responsible_person=self.coordinator,
            antal_par=24
        )
        
        self.assignment = UserSubstitutAssignment.objects.create(
            user=self.regular_user,
            substitutliste=self.substitutliste,
            status='Ledig'
        )

    def test_front_page_loads(self):
        """Test that the front page loads successfully."""
        response = self.client.get(reverse('front_page'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'front_page.html')
        self.assertContains(response, "Welcome to test site")

    def test_substitutlister_page_loads(self):
        """Test that the substitutlister page loads successfully."""
        response = self.client.get(reverse('substitutlister'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'substitutlister.html')

    def test_afmeldingslister_page_loads(self):
        """Test that the afmeldingslister page loads successfully."""
        response = self.client.get(reverse('afmeldingslister'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'afmeldingslister.html')

    def test_append_afbud_adds_name(self):
        """Test adding a new absence name."""
        # Login as admin
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

    def test_append_afbud_duplicate_name(self):
        """Test adding a duplicate absence name."""
        # Login as admin
        self.client.login(username='admin', password='admin123')
        
        # Add first absence
        self.afmeldingsliste.names = 'John Doe'
        self.afmeldingsliste.save()
        
        # Try to add same name again
        response = self.client.post(
            reverse('append_afbud', args=[self.afmeldingsliste.id]),
            {'name': 'John Doe'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertFalse(data['success'])
        self.assertEqual(data['error'], 'Name already exists in the list')

    def test_append_afbud_empty_name(self):
        """Test adding an empty absence name."""
        # Login as admin
        self.client.login(username='admin', password='admin123')
        
        response = self.client.post(
            reverse('append_afbud', args=[self.afmeldingsliste.id]),
            {'name': ''},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertFalse(data['success'])
        self.assertEqual(data['error'], 'Name cannot be empty')

    def test_append_afbud_invalid_id(self):
        """Test adding absence to non-existent list."""
        # Login as admin
        self.client.login(username='admin', password='admin123')
        
        response = self.client.post(
            reverse('append_afbud', args=[999]),  # Non-existent ID
            {'name': 'John Doe'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.content)
        self.assertFalse(data['success'])
        self.assertEqual(data['error'], 'List not found')

    def test_append_afbud_not_ajax(self):
        """Test adding absence without AJAX."""
        # Login as admin
        self.client.login(username='admin', password='admin123')
        
        response = self.client.post(
            reverse('append_afbud', args=[self.afmeldingsliste.id]),
            {'name': 'John Doe'}
        )
        
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content.decode(), 'Only AJAX requests are allowed')

    def test_append_afbud_past_deadline(self):
        """Test adding absence after deadline."""
        # Login as admin
        self.client.login(username='admin', password='admin123')
        
        # Set deadline to past date
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

    def test_append_afbud_success(self):
        """Test successfully adding an absence."""
        # Login as admin
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

    def test_append_afbud_duplicate(self):
        """Test adding a duplicate absence name."""
        # Login as admin
        self.client.login(username='admin', password='admin123')
        
        # Add first absence
        self.client.post(
            reverse('append_afbud', args=[self.afmeldingsliste.id]),
            {'name': 'John Doe'},
            content_type='application/json'
        )
        
        # Try to add the same name again
        response = self.client.post(
            reverse('append_afbud', args=[self.afmeldingsliste.id]),
            {'name': 'John Doe'},
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], 'Name already exists in the list')

    def test_append_afbud_invalid_id(self):
        """Test adding absence to non-existent list."""
        # Login as admin
        self.client.login(username='admin', password='admin123')
        
        response = self.client.post(
            reverse('append_afbud', args=[999]),  # Non-existent ID
            {'name': 'John Doe'},
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 404)

    def test_append_afbud_missing_name(self):
        """Test adding absence without a name."""
        # Login as admin
        self.client.login(username='admin', password='admin123')
        
        response = self.client.post(
            reverse('append_afbud', args=[self.afmeldingsliste.id]),
            {},  # Empty data
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], 'Name is required')

    def test_append_afbud_past_deadline(self):
        """Test adding absence after deadline."""
        # Login as admin
        self.client.login(username='admin', password='admin123')
        
        # Set deadline to past date
        self.afmeldingsliste.deadline = timezone.now() - timezone.timedelta(days=1)
        self.afmeldingsliste.save()
        
        response = self.client.post(
            reverse('append_afbud', args=[self.afmeldingsliste.id]),
            {'name': 'John Doe'},
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], 'Deadline has passed')

    def test_append_afbud_unauthorized(self):
        """Test adding absence without authentication."""
        response = self.client.post(
            reverse('append_afbud', args=[self.afmeldingsliste.id]),
            {'name': 'John Doe'},
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 302)  # Redirect to login
        self.assertTrue(response.url.startswith('/admin/login/')) 

    def test_front_page_context(self):
        """Test that front page has all required context data."""
        # Create test data
        week = Week.objects.create(name="2-2024")
        monday, _ = Day.objects.get_or_create(name="Monday")
        tuesday, _ = Day.objects.get_or_create(name="Tuesday")
        
        # Create a coordinator
        coordinator = CustomUser.objects.create_user(
            username="coordinator_front_page",
            email="coord_front@test.com",
            password="pass123",
            first_name="John",
            last_name="Coordinator",
            user_type="Substitutter",
            phone_number="+45 11111111"
        )
        
        # Create day responsibility
        responsibility = DayResponsibility.objects.create(
            day=monday,
            coordinator=coordinator
        )
        
        # Create a substitut
        substitut = CustomUser.objects.create_user(
            username="substitut_front_page",
            email="sub_front@test.com",
            password="pass123",
            user_type="Substitutter",
            phone_number="+45 12345678",
            custom_note="Test note",
            række=self.række
        )
        
        # Create a substitutliste
        test_date = timezone.now()
        substitutliste = Substitutliste.objects.create(
            name="Monday List",
            day=test_date,
            deadline=test_date + timezone.timedelta(days=1),
            week=week
        )
        
        # Create an assignment
        assignment = UserSubstitutAssignment.objects.create(
            user=substitut,
            substitutliste=substitutliste,
            status='Ledig'
        )
        
        # Get the front page
        response = self.client.get(reverse('front_page'))
        
        # Test response
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'front_page.html')
        
        # Test context data
        self.assertIn('welcome_text', response.context)
        self.assertEqual(response.context['welcome_text'], 'Welcome to test site')
        
        # Test substitutlister in context
        self.assertIn('substitutlister', response.context)
        substitutlister = response.context['substitutlister']
        self.assertEqual(len(substitutlister), 2)  # One from setUp, one from test
        
        # Find the specific list created in this test
        monday_list = next((lst for lst in substitutlister if lst.name == "Monday List"), None)
        self.assertIsNotNone(monday_list, "Monday List not found in substitutlister")
        self.assertEqual(monday_list.responsible_name, "John Coordinator")
        self.assertEqual(monday_list.responsible_email, "coord_front@test.com")
        
        # Test assigned substitutter
        self.assertTrue(hasattr(monday_list, 'assigned_substitutter'))
        self.assertEqual(len(monday_list.assigned_substitutter), 1)
        
        assigned = monday_list.assigned_substitutter[0]
        self.assertEqual(assigned['name'], 'substitut_front_page')
        self.assertEqual(assigned['phone'], '+45 12345678')
        self.assertEqual(assigned['note'], 'Test note')
        self.assertEqual(assigned['email'], 'sub_front@test.com')
        self.assertEqual(assigned['status'], 'Ledig')
        self.assertEqual(assigned['række'], 'A-række')
        
        # Test weeks in context
        self.assertIn('weeks', response.context)
        weeks = response.context['weeks']
        self.assertEqual(len(weeks), 1)
        self.assertEqual(weeks[0].name, "2-2024")
        
        # Test days in context
        self.assertIn('days', response.context)
        days = response.context['days']
        self.assertEqual(len(days), 2)
        day_names = [day.name for day in days]
        self.assertIn('Monday', day_names)
        self.assertIn('Tuesday', day_names)
        
        # Test day name mapping
        self.assertIn('day_name_mapping', response.context)
        mapping = response.context['day_name_mapping']
        self.assertEqual(mapping['Monday'], 'Mandag')
        self.assertEqual(mapping['Tuesday'], 'Tirsdag')

    def test_front_page_no_configuration(self):
        """Test front page behavior when no configuration exists."""
        Configuration.objects.all().delete()
        response = self.client.get(reverse('front_page'))
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['welcome_text'], '')

    def test_front_page_no_coordinator(self):
        """Test front page when a day has no coordinator assigned."""
        # Remove the existing day responsibility to test no coordinator case
        DayResponsibility.objects.all().delete()
        
        week = Week.objects.create(name="2-2024")
        monday, _ = Day.objects.get_or_create(name="Monday")
        
        test_date = timezone.now()
        substitutliste = Substitutliste.objects.create(
            name="Monday List",
            day=test_date,
            deadline=test_date + timezone.timedelta(days=1),
            week=week
        )
        
        response = self.client.get(reverse('front_page'))
        
        self.assertEqual(response.status_code, 200)
        substitutlister = response.context['substitutlister']
        first_list = substitutlister[0]
        self.assertEqual(first_list.responsible_name, "Not assigned")
        self.assertEqual(first_list.responsible_email, "")

    def test_front_page_week_sorting(self):
        """Test that weeks are properly sorted by week number."""
        Week.objects.create(name="2-2024")
        Week.objects.create(name="1-2024")
        Week.objects.create(name="3-2024")
        
        response = self.client.get(reverse('front_page'))
        
        weeks = response.context['weeks']
        week_names = [week.name for week in weeks]
        self.assertEqual(week_names, ["1-2024", "2-2024", "3-2024"]) 

    def test_select_substitut_get(self):
        """Test GET request to select_substitut view."""
        response = self.client.get(reverse('select_substitut'))
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertFalse(data['success'])
        self.assertEqual(data['error'], 'Invalid request method')

    def test_select_substitut_post_success(self):
        """Test successful POST request to select_substitut view."""
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

    def test_select_substitut_post_invalid_assignment(self):
        """Test POST request with invalid assignment ID."""
        response = self.client.post(
            reverse('select_substitut'),
            {
                'assignment_id': 999,  # Non-existent ID
                'action': 'reserve',
                'note': 'Test reservation'
            },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.content)
        self.assertFalse(data['success'])
        self.assertEqual(data['error'], 'Assignment not found')

    def test_select_substitut_post_invalid_action(self):
        """Test POST request with invalid action."""
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

    def test_select_substitut_post_already_reserved(self):
        """Test POST request for already reserved assignment."""
        # First reserve the assignment
        self.assignment.status = 'Optaget'
        self.assignment.save()
        
        response = self.client.post(
            reverse('select_substitut'),
            {
                'assignment_id': self.assignment.id,
                'action': 'reserve',
                'note': 'Test reservation'
            },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertFalse(data['success'])
        self.assertEqual(data['error'], 'Assignment is already reserved')

    def test_select_substitut_post_past_deadline(self):
        """Test POST request after deadline has passed."""
        # Set deadline to past
        self.substitutliste.deadline = timezone.now() - timezone.timedelta(days=1)
        self.substitutliste.save()
        
        response = self.client.post(
            reverse('select_substitut'),
            {
                'assignment_id': self.assignment.id,
                'action': 'reserve',
                'note': 'Test reservation'
            },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertFalse(data['success'])
        self.assertEqual(data['error'], 'Deadline er overskredet')

    def test_afmeldingsliste_detail_get(self):
        """Test GET request to afmeldingsliste_detail view."""
        # Create test data
        test_date = timezone.now()
        afmeldingsliste = Afmeldingsliste.objects.create(
            name="Test List",
            day=test_date,
            deadline=test_date + timezone.timedelta(days=1),
            names=['John Doe', 'Jane Smith']
        )
        
        # Get the page
        response = self.client.get(reverse('afmeldingsliste_detail', args=[afmeldingsliste.id]))
        
        # Test response
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'afmeldingsliste_detail.html')
        
        # Test context data
        self.assertIn('afmeldingsliste', response.context)
        self.assertEqual(response.context['afmeldingsliste'], afmeldingsliste)
        
        self.assertIn('names', response.context)
        names = response.context['names']
        self.assertEqual(len(names), 2)
        self.assertIn('John Doe', names)
        self.assertIn('Jane Smith', names)

    def test_afmeldingsliste_detail_invalid_id(self):
        """Test GET request with invalid afmeldingsliste ID."""
        response = self.client.get(reverse('afmeldingsliste_detail', args=[999]))  # Non-existent ID
        self.assertEqual(response.status_code, 404)

    def test_afmeldingsliste_detail_empty_list(self):
        """Test GET request for afmeldingsliste with no names."""
        # Create test data
        test_date = timezone.now()
        afmeldingsliste = Afmeldingsliste.objects.create(
            name="Empty List",
            day=test_date,
            deadline=test_date + timezone.timedelta(days=1),
            names=[]
        )
        
        # Get the page
        response = self.client.get(reverse('afmeldingsliste_detail', args=[afmeldingsliste.id]))
        
        # Test response
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'afmeldingsliste_detail.html')
        
        # Test context data
        self.assertIn('names', response.context)
        names = response.context['names']
        self.assertEqual(len(names), 0)

    def test_afmeldingsliste_detail_past_deadline(self):
        """Test GET request for afmeldingsliste after deadline."""
        # Create test data
        test_date = timezone.now()
        afmeldingsliste = Afmeldingsliste.objects.create(
            name="Past Deadline List",
            day=test_date,
            deadline=test_date - timezone.timedelta(days=1),  # Past deadline
            names=['John Doe']
        )
        
        # Get the page
        response = self.client.get(reverse('afmeldingsliste_detail', args=[afmeldingsliste.id]))
        
        # Test response
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'afmeldingsliste_detail.html')
        
        # Test context data
        self.assertIn('afmeldingsliste', response.context)
        self.assertTrue(response.context['afmeldingsliste'].is_past_deadline)

    def test_afmeldingsliste_detail_sorted_names(self):
        """Test that names are sorted alphabetically."""
        # Create test data
        test_date = timezone.now()
        afmeldingsliste = Afmeldingsliste.objects.create(
            name="Test List",
            day=test_date,
            deadline=test_date + timezone.timedelta(days=1),
            names=['Zoe Brown', 'Adam Smith', 'John Doe']
        )
        
        # Get the page
        response = self.client.get(reverse('afmeldingsliste_detail', args=[afmeldingsliste.id]))
        
        # Test response
        self.assertEqual(response.status_code, 200)
        
        # Test that names are sorted
        names = response.context['names']
        self.assertEqual(names, ['Adam Smith', 'John Doe', 'Zoe Brown']) 

    def test_substitutlister_get(self):
        """Test GET request to substitutlister view."""
        # Create test data
        week = Week.objects.create(name="2-2024")
        monday, _ = Day.objects.get_or_create(name="Monday")
        
        # Create a coordinator
        coordinator = CustomUser.objects.create_user(
            username="coordinator_sub_list",
            email="coord_sub@test.com",
            password="pass123",
            first_name="John",
            last_name="Coordinator",
            user_type="Substitutter",
            phone_number="+45 11111111"
        )
        
        # Create day responsibility
        responsibility = DayResponsibility.objects.create(
            day=monday,
            coordinator=coordinator
        )
        
        # Create a substitut
        substitut = CustomUser.objects.create_user(
            username="substitut_sub_list",
            email="sub_sub@test.com",
            password="pass123",
            user_type="Substitutter",
            phone_number="+45 12345678",
            custom_note="Test note",
            række=self.række
        )
        
        # Create a substitutliste
        test_date = timezone.now()
        substitutliste = Substitutliste.objects.create(
            name="Monday List",
            day=test_date,
            deadline=test_date + timezone.timedelta(days=1),
            week=week
        )
        
        # Create an assignment
        assignment = UserSubstitutAssignment.objects.create(
            user=substitut,
            substitutliste=substitutliste,
            status='Ledig'
        )
        
        # Get the page
        response = self.client.get(reverse('substitutlister'))
        
        # Test response
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'substitutlister.html')
        
        # Test context data
        self.assertIn('substitutlister', response.context)
        substitutlister = response.context['substitutlister']
        self.assertEqual(len(substitutlister), 2)  # One from setUp, one from test
        
        # Find the specific list created in this test
        monday_list = next((lst for lst in substitutlister if lst.name == "Monday List"), None)
        self.assertIsNotNone(monday_list, "Monday List not found in substitutlister")
        self.assertEqual(monday_list.responsible_name, "John Coordinator")
        self.assertEqual(monday_list.responsible_email, "coord_sub@test.com")
        
        # Test assigned substitutter
        self.assertTrue(hasattr(monday_list, 'assigned_substitutter'))
        self.assertEqual(len(monday_list.assigned_substitutter), 1)
        
        assigned = monday_list.assigned_substitutter[0]
        self.assertEqual(assigned['name'], 'substitut_sub_list')
        self.assertEqual(assigned['phone'], '+45 12345678')
        self.assertEqual(assigned['note'], 'Test note')
        self.assertEqual(assigned['email'], 'sub_sub@test.com')
        self.assertEqual(assigned['status'], 'Ledig')
        self.assertEqual(assigned['række'], 'A-række')

    def test_substitutlister_no_configuration(self):
        """Test substitutlister view when no configuration exists."""
        Configuration.objects.all().delete()
        response = self.client.get(reverse('substitutlister'))
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['substitutlister_text'], '')

    def test_substitutlister_no_coordinator(self):
        """Test substitutlister view when a day has no coordinator assigned."""
        week = Week.objects.create(name="2-2024")
        monday, _ = Day.objects.get_or_create(name="Monday")
        
        test_date = timezone.now()
        substitutliste = Substitutliste.objects.create(
            name="Monday List",
            day=test_date,
            deadline=test_date + timezone.timedelta(days=1),
            week=week
        )
        
        response = self.client.get(reverse('substitutlister'))
        
        self.assertEqual(response.status_code, 200)
        substitutlister = response.context['substitutlister']
        first_list = substitutlister[0]
        self.assertEqual(first_list.responsible_name, "Not assigned")
        self.assertEqual(first_list.responsible_email, "")

    def test_substitutlister_week_sorting(self):
        """Test that weeks are properly sorted by week number."""
        Week.objects.create(name="2-2024")
        Week.objects.create(name="1-2024")
        Week.objects.create(name="3-2024")
        
        response = self.client.get(reverse('substitutlister'))
        
        weeks = response.context['weeks']
        week_names = [week.name for week in weeks]
        self.assertEqual(week_names, ["1-2024", "2-2024", "3-2024"])

    def test_substitutlister_day_name_mapping(self):
        """Test that day names are properly mapped to Danish."""
        response = self.client.get(reverse('substitutlister'))
        
        self.assertIn('day_name_mapping', response.context)
        mapping = response.context['day_name_mapping']
        self.assertEqual(mapping['Monday'], 'Mandag')
        self.assertEqual(mapping['Tuesday'], 'Tirsdag')
        self.assertEqual(mapping['Wednesday'], 'Onsdag')
        self.assertEqual(mapping['Thursday'], 'Torsdag')
        self.assertEqual(mapping['Friday'], 'Fredag')
        self.assertEqual(mapping['Saturday'], 'Lørdag')
        self.assertEqual(mapping['Sunday'], 'Søndag') 

    def test_afmeldingslister_get(self):
        """Test GET request to afmeldingslister view."""
        # Create test data
        test_date = timezone.now()
        afmeldingsliste1 = Afmeldingsliste.objects.create(
            name="List 1",
            day=test_date,
            deadline=test_date + timezone.timedelta(days=1),
            names=['John Doe', 'Jane Smith']
        )
        
        afmeldingsliste2 = Afmeldingsliste.objects.create(
            name="List 2",
            day=test_date + timezone.timedelta(days=1),
            deadline=test_date + timezone.timedelta(days=2),
            names=['Bob Wilson']
        )
        
        # Get the page
        response = self.client.get(reverse('afmeldingslister'))
        
        # Test response
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'afmeldingslister.html')
        
        # Test context data
        self.assertIn('afmeldingslister', response.context)
        afmeldingslister = response.context['afmeldingslister']
        self.assertEqual(len(afmeldingslister), 2)
        
        # Test lists are ordered by day
        self.assertEqual(afmeldingslister[0], afmeldingsliste1)
        self.assertEqual(afmeldingslister[1], afmeldingsliste2)
        
        # Test configuration text
        self.assertIn('afmeldingslister_text', response.context)
        self.assertEqual(response.context['afmeldingslister_text'], 'Default text')

    def test_afmeldingslister_no_configuration(self):
        """Test afmeldingslister view when no configuration exists."""
        Configuration.objects.all().delete()
        response = self.client.get(reverse('afmeldingslister'))
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['afmeldingslister_text'], '')

    def test_afmeldingslister_empty(self):
        """Test afmeldingslister view with no lists."""
        # Delete any existing lists
        Afmeldingsliste.objects.all().delete()
        
        response = self.client.get(reverse('afmeldingslister'))
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['afmeldingslister']), 0)

    def test_afmeldingslister_past_deadline(self):
        """Test afmeldingslister view with lists past deadline."""
        test_date = timezone.now()
        afmeldingsliste = Afmeldingsliste.objects.create(
            name="Past Deadline List",
            day=test_date,
            deadline=test_date - timezone.timedelta(days=1),  # Past deadline
            names=['John Doe']
        )
        
        response = self.client.get(reverse('afmeldingslister'))
        
        self.assertEqual(response.status_code, 200)
        lists = response.context['afmeldingslister']
        self.assertEqual(len(lists), 1)
        self.assertTrue(lists[0].is_past_deadline)

    def test_afmeldingslister_sorting(self):
        """Test that afmeldingslister are properly sorted by day."""
        test_date = timezone.now()
        
        # Create lists in non-chronological order
        list3 = Afmeldingsliste.objects.create(
            name="List 3",
            day=test_date + timezone.timedelta(days=2),
            deadline=test_date + timezone.timedelta(days=3)
        )
        
        list1 = Afmeldingsliste.objects.create(
            name="List 1",
            day=test_date,
            deadline=test_date + timezone.timedelta(days=1)
        )
        
        list2 = Afmeldingsliste.objects.create(
            name="List 2",
            day=test_date + timezone.timedelta(days=1),
            deadline=test_date + timezone.timedelta(days=2)
        )
        
        response = self.client.get(reverse('afmeldingslister'))
        
        lists = response.context['afmeldingslister']
        self.assertEqual(len(lists), 3)
        self.assertEqual(lists[0], list1)  # Earliest date first
        self.assertEqual(lists[1], list2)
        self.assertEqual(lists[2], list3)  # Latest date last 

    def test_tilmeldingslister_get(self):
        """Test GET request to tilmeldingslister view."""
        test_date = timezone.now()
        tilmeldingsliste1 = Tilmeldingsliste.objects.create(
            name="List 1",
            day=test_date,
            deadline=test_date + timezone.timedelta(days=1),
            responsible_person=self.coordinator,
            antal_par=24
        )
        
        tilmeldingsliste2 = Tilmeldingsliste.objects.create(
            name="List 2",
            day=test_date + timezone.timedelta(days=1),
            deadline=test_date + timezone.timedelta(days=2),
            responsible_person=self.coordinator,
            antal_par=24
        )
        
        # Create pairs for first list
        pair1 = TilmeldingslistePair.objects.create(
            tilmeldingsliste=tilmeldingsliste1,
            navn="John Doe",
            makker="Jane Smith",
            telefonnummer="+45 12345678",
            email="john@example.com",
            parnummer=1
        )
        
        pair2 = TilmeldingslistePair.objects.create(
            tilmeldingsliste=tilmeldingsliste1,
            navn="Bob Wilson",
            makker="Alice Brown",
            telefonnummer="+45 87654321",
            email="bob@example.com",
            parnummer=2
        )
        
        # Create a waiting list pair
        waiting_pair = TilmeldingslistePair.objects.create(
            tilmeldingsliste=tilmeldingsliste1,
            navn="Wait Person",
            makker="Wait Partner",
            telefonnummer="+45 11111111",
            email="wait@example.com",
            på_venteliste=True
        )
        
        # Create a single player
        single_player = TilmeldingslistePair.objects.create(
            tilmeldingsliste=tilmeldingsliste1,
            navn="Single Player",
            telefonnummer="+45 22222222",
            email="single@example.com",
            is_single=True
        )
        
        # Get the page
        response = self.client.get(reverse('tilmeldingslister'))
        
        # Test response
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tilmeldingslister.html')
        
        # Test context data
        self.assertIn('tilmeldingslister', response.context)
        tilmeldingslister = response.context['tilmeldingslister']
        self.assertEqual(len(tilmeldingslister), 2)
        
        # Test first list
        first_list = tilmeldingslister[0]
        self.assertEqual(first_list.name, "List 1")
        
        # Test regular pairs
        self.assertEqual(len(first_list.tilmeldte_par), 2)
        self.assertEqual(first_list.tilmeldte_par[0].parnummer, 1)
        self.assertEqual(first_list.tilmeldte_par[1].parnummer, 2)
        
        # Test waiting list
        self.assertEqual(len(first_list.venteliste_par), 1)
        self.assertTrue(first_list.venteliste_par[0].på_venteliste)
        
        # Test single players
        self.assertEqual(len(first_list.single_players), 1)
        self.assertTrue(first_list.single_players[0].is_single)
        
        # Test configuration text
        self.assertIn('tilmeldingslister_text', response.context)
        self.assertEqual(response.context['tilmeldingslister_text'], 'Default text')

    def test_tilmeldingslister_no_configuration(self):
        """Test tilmeldingslister view when no configuration exists."""
        Configuration.objects.all().delete()
        response = self.client.get(reverse('tilmeldingslister'))
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['tilmeldingslister_text'], '')

    def test_tilmeldingslister_empty(self):
        """Test tilmeldingslister view with no lists."""
        # Delete any existing lists
        Tilmeldingsliste.objects.all().delete()
        
        response = self.client.get(reverse('tilmeldingslister'))
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['tilmeldingslister']), 0)
        self.assertIsNone(response.context.get('selected_list'))

    def test_tilmeldingslister_selected_list(self):
        """Test tilmeldingslister view with selected list."""
        test_date = timezone.now()
        tilmeldingsliste = Tilmeldingsliste.objects.create(
            name="Selected List",
            day=test_date,
            deadline=test_date + timezone.timedelta(days=1),
            responsible_person=self.coordinator,
            antal_par=24
        )
        
        # Get the page with selected list
        response = self.client.get(
            reverse('tilmeldingslister'),
            {'selected_list_id': tilmeldingsliste.id}
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['selected_list'], tilmeldingsliste)

    def test_tilmeldingslister_default_selection(self):
        """Test that oldest list is selected by default."""
        test_date = timezone.now()
        
        # Create lists in non-chronological order
        list2 = Tilmeldingsliste.objects.create(
            name="List 2",
            day=test_date + timezone.timedelta(days=1),
            deadline=test_date + timezone.timedelta(days=2),
            responsible_person=self.coordinator,
            antal_par=24
        )
        
        list1 = Tilmeldingsliste.objects.create(
            name="List 1",
            day=test_date,  # Earlier date
            deadline=test_date + timezone.timedelta(days=1),
            responsible_person=self.coordinator,
            antal_par=24
        )
        
        response = self.client.get(reverse('tilmeldingslister'))
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['selected_list'], list1)  # Earlier list should be selected

    def test_tilmeldingslister_sorting(self):
        """Test that lists and pairs are properly sorted."""
        test_date = timezone.now()
        
        # Create lists in non-chronological order
        list2 = Tilmeldingsliste.objects.create(
            name="List 2",
            day=test_date + timezone.timedelta(days=1),
            deadline=test_date + timezone.timedelta(days=2),
            responsible_person=self.coordinator,
            antal_par=24
        )
        
        list1 = Tilmeldingsliste.objects.create(
            name="List 1",
            day=test_date,
            deadline=test_date + timezone.timedelta(days=1),
            responsible_person=self.coordinator,
            antal_par=24
        )
        
        # Create pairs in non-sequential order
        pair2 = TilmeldingslistePair.objects.create(
            tilmeldingsliste=list1,
            navn="Pair 2",
            makker="Partner 2",
            parnummer=2
        )
        
        pair1 = TilmeldingslistePair.objects.create(
            tilmeldingsliste=list1,
            navn="Pair 1",
            makker="Partner 1",
            parnummer=1
        )
        
        response = self.client.get(reverse('tilmeldingslister'))
        
        # Test list sorting
        tilmeldingslister = response.context['tilmeldingslister']
        self.assertEqual(tilmeldingslister[0], list1)  # Earlier date first
        self.assertEqual(tilmeldingslister[1], list2)
        
        # Test pair sorting
        pairs = tilmeldingslister[0].tilmeldte_par
        self.assertEqual(pairs[0], pair1)  # Lower number first
        self.assertEqual(pairs[1], pair2) 