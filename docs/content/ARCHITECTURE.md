# Project Architecture

Technical overview of the Bridge Club Management System structure, models, and components.

## 🏗️ Project Structure

```
bridge_club_management/
├── bridge_club_management/              # Django project configuration
│   ├── settings/                       # Environment-specific settings
│   │   ├── __init__.py
│   │   ├── base.py                     # Shared settings
│   │   ├── local.py                    # Local development
│   │   ├── develop.py                  # Development server
│   │   └── production.py               # Production settings
│   ├── __init__.py
│   ├── asgi.py                         # ASGI configuration
│   ├── urls.py                         # Root URL configuration
│   └── wsgi.py                         # WSGI configuration
│
├── club_management/                     # Main Django application
│   ├── management/                     # Custom management commands
│   │   └── commands/
│   │       ├── create_days.py
│   │       ├── ensure_substitutlister.py
│   │       ├── update_day_names.py
│   │       ├── update_substitution_lists.py
│   │       └── update_weeks.py
│   ├── migrations/                     # Database migrations
│   ├── templates/                      # HTML templates
│   ├── templatetags/                   # Custom template tags
│   ├── admin.py                        # Django admin configuration
│   ├── apps.py                         # App configuration
│   ├── forms.py                        # Django forms
│   ├── models.py                       # Database models
│   ├── signals.py                      # Django signals
│   ├── urls.py                         # App URL patterns
│   └── views.py                        # View functions
│
├── static/                             # Static files (CSS, JS, images)
├── media/                              # User-uploaded files
├── requirements/                       # Python dependencies
├── templates/                          # Global templates (if any)
└── manage.py                          # Django management script
```

## 🗄️ Database Models

### Core Models

#### CustomUser
**Purpose**: Extended user model for club members
```python
class CustomUser(AbstractUser):
    user_type = models.CharField(max_length=20)
    phone_number = models.CharField(max_length=15)
    række = models.IntegerField()  # Row number
    custom_note = models.TextField()
```

**Key Features**:
- Extends Django's built-in User model
- Tracks user type (member, substitute, admin)
- Stores contact information
- Manages seating arrangements (række/row)

#### Day
**Purpose**: Represents days of the week for scheduling
```python
class Day(models.Model):
    name = models.CharField(max_length=20)
    # Day names in Danish/English
```

#### Week  
**Purpose**: Represents calendar weeks
```python
class Week(models.Model):
    year = models.IntegerField()
    week_number = models.IntegerField()
    start_date = models.DateField()
    end_date = models.DateField()
```

#### Substitutliste (Substitute List)
**Purpose**: Core model for substitute scheduling
```python
class Substitutliste(models.Model):
    name = models.CharField(max_length=100)
    day = models.ForeignKey(Day)
    week = models.ForeignKey(Week)
    substitutes = models.ManyToManyField(CustomUser, through='UserSubstitutAssignment')
```

**Key Features**:
- Links days and weeks for scheduling
- Many-to-many relationship with users through assignments
- Automatically managed by management commands

#### UserSubstitutAssignment
**Purpose**: Junction table with additional data for substitute assignments
```python
class UserSubstitutAssignment(models.Model):
    user = models.ForeignKey(CustomUser)
    substitutliste = models.ForeignKey(Substitutliste)
    status = models.CharField(max_length=20)
    reservationsnote = models.TextField()
    
    class StatusChoices:
        AVAILABLE = 'available'
        CHOSEN = 'chosen'
        UNAVAILABLE = 'unavailable'
```

#### DayResponsibility
**Purpose**: Assigns coordinators to specific days
```python
class DayResponsibility(models.Model):
    day = models.ForeignKey(Day)
    coordinator = models.ForeignKey(CustomUser)
```

#### Afmeldingsliste (Absence List)
**Purpose**: Tracks member absences
```python
class Afmeldingsliste(models.Model):
    name = models.CharField(max_length=100)
    day = models.DateField()
    deadline = models.DateTimeField()
    framed_users = models.ManyToManyField(CustomUser)
```

#### Tilmeldingsliste (Registration List)  
**Purpose**: Event registration management
```python
class Tilmeldingsliste(models.Model):
    name = models.CharField(max_length=100)
    day = models.DateField()
    deadline = models.DateTimeField()
    responsible_person = models.ForeignKey(CustomUser)
    antal_par = models.IntegerField()  # Number of pairs
```

### Model Relationships

```
CustomUser ←→ UserSubstitutAssignment ←→ Substitutliste
    ↓                                        ↑
DayResponsibility                           Day
    ↓                                        ↑
   Day ←→ Week ←→ Substitutliste

CustomUser ←→ Afmeldingsliste
CustomUser → Tilmeldingsliste (responsible_person)
```

## 🎨 Frontend Architecture

### Templates Structure
```
templates/
├── base.html                    # Base template (if exists)
├── afmeldingslister.html       # Absence lists
├── front_page.html             # Homepage
├── login.html                  # Login page
├── navbar.html                 # Navigation component
├── substitutlister.html        # Substitute lists
└── tilmeldingslister.html      # Registration lists
```

### Static Files Organization
```
static/
├── admin/                      # Django admin static files
├── bootstrap_datepicker_plus/  # Date picker component
├── ckeditor/                   # Rich text editor
├── django_ckeditor_5/          # CKEditor 5
└── scripts.js                  # Custom JavaScript
```

### Frontend Technologies
- **HTML5**: Semantic markup
- **CSS3**: Styling with Bootstrap framework
- **JavaScript**: Interactive functionality
- **Bootstrap**: Responsive design framework
- **CKEditor 5**: Rich text editing
- **Bootstrap DatePicker**: Date selection

## 🔧 Django Configuration

### Settings Architecture
```python
# base.py - Shared configuration
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    # ... other Django apps
    'club_management.apps.ClubManagementConfig',
    'django_ckeditor_5',
    'bootstrap_datepicker_plus',
]

# Environment-specific overrides in local.py, develop.py, production.py
DEBUG = True/False
DATABASES = {...}
EMAIL_BACKEND = '...'
```

### URL Structure
```python
# Root urls.py
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('club_management.urls')),
]

# club_management/urls.py
urlpatterns = [
    path('', views.front_page, name='front_page'),
    path('substitutlister/', views.substitutlister, name='substitutlister'),
    path('afmeldingslister/', views.afmeldingslister, name='afmeldingslister'),
    path('tilmeldingslister/', views.tilmeldingslister, name='tilmeldingslister'),
    # ... other patterns
]
```

## 📊 Data Flow

### Substitute List Management
```
1. Management Commands → Create Week/Day records
2. Substitutliste created → Links Day + Week  
3. Users assigned → UserSubstitutAssignment created
4. User updates status → Assignment status changed
5. Coordinator notified → Email sent via Django signals
```

### User Workflow
```
User Login → View Lists → Select/Update Status → Email Notifications
     ↓
Admin Interface → Manage Users/Lists → System Updates
```

## 🛠️ Custom Management Commands

### Automated Maintenance
- **`create_days.py`**: Ensures all weekdays exist
- **`ensure_substitutlister.py`**: Creates substitute lists for current week
- **`update_day_names.py`**: Updates day name localization
- **`update_substitution_lists.py`**: Refreshes substitute assignments
- **`update_weeks.py`**: Creates upcoming week records

### Scheduled Execution
These commands are designed to run daily via cron jobs:
```bash
# Daily maintenance (example cron job)
0 2 * * * cd /path/to/project && python manage.py ensure_substitutlister
```

## 🔐 Authentication & Authorization

### User Types
- **Admin**: Full system access
- **Coordinator**: Can manage specific day assignments
- **Member**: Can view and update their own assignments
- **Substitute**: Can update availability status

### Permissions
- Django's built-in permission system
- Custom user types in models
- Template-based access control
- Admin interface permissions

## 📧 Email System

### Email Notifications
- **Trigger**: User status changes in assignments
- **Recipients**: Day coordinators
- **Content**: User selection notifications
- **Backend**: SMTP (production), Console (development)

### Signal-Based Processing
```python
# signals.py
@receiver(post_save, sender=UserSubstitutAssignment)
def notify_coordinator(sender, instance, **kwargs):
    # Send email to responsible coordinator
```

## 🎛️ Admin Interface

### Custom Admin Configuration
- Enhanced user management
- Bulk operations for substitute lists
- Inline editing for assignments
- Custom actions for list management

### Admin Features
- User creation with automatic permissions
- Substitute list bulk updates
- Assignment status management
- Absence list administration

## 🔍 Performance Considerations

### Database Optimization
- Proper foreign key relationships
- Strategic use of `select_related()` and `prefetch_related()`
- Database indexing on frequently queried fields

### Caching Strategy
- Django's built-in caching framework ready
- Static file optimization
- Template fragment caching potential

### Scalability
- Separate databases for different environments
- Static file serving optimization
- Database connection pooling ready

## 🧪 Testing Architecture

### Test Structure (Ready for Implementation)
```python
# tests/
├── test_models.py          # Model testing
├── test_views.py           # View testing  
├── test_forms.py           # Form validation testing
├── test_commands.py        # Management command testing
└── test_integration.py     # End-to-end testing
```

### Testing Strategy
- Unit tests for models and business logic
- Integration tests for workflows
- Functional tests for user interactions
- Management command testing

## 🔄 Development Workflow Integration

### Git Integration
- Feature branch development
- Automated testing on commits
- Environment-specific deployments

### CI/CD Ready
- GitHub Actions workflows defined
- Automated testing pipeline
- Deployment automation

---
*This architecture supports the club's needs while remaining maintainable and scalable for future enhancements.*