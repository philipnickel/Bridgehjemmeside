# Bridge Club Management System

A Django web application for managing bridge club substitute lists, member registration, and event coordination.

## 🚀 Quick Start

```bash
# Clone and setup
git clone https://github.com/philipnickel/Bridgehjemmeside.git
cd Bridgehjemmeside/bridge_club_management

# Install dependencies
pip install -r requirements/local.txt

# Setup environment
cp env.template .env
# Edit .env with your settings

# Initialize database
python manage.py migrate
python manage.py createsuperuser

# Run development server
python manage.py runserver
```

**Local site**: http://localhost:8000

## 📁 Project Structure

```
Bridgehjemmeside/
├── bridge_club_management/          # Django project
│   ├── bridge_club_management/      # Project settings
│   │   └── settings/               # Environment-specific settings
│   ├── club_management/            # Main Django app
│   │   ├── models.py              # Database models
│   │   ├── views.py               # Request handlers
│   │   ├── forms.py               # Form definitions
│   │   ├── admin.py               # Admin interface
│   │   ├── templates/             # HTML templates
│   │   └── tests/                 # Test files
│   ├── requirements/              # Dependency files
│   └── scripts/                   # Utility scripts
├── docs/                          # Documentation
└── .github/workflows/             # CI/CD workflows
```

## 🌟 Key Features

- **Substitute Management**: Automated substitute list generation
- **User Management**: Custom user system with availability tracking  
- **Event Registration**: Registration with waitlists and notifications
- **Admin Interface**: Django admin with custom configurations
- **Multi-Environment**: Local development, staging, and production setups

## 🔧 Technology Stack

- **Backend**: Django 4.2+, Python 3.11
- **Database**: SQLite (local), MySQL (production)
- **Frontend**: HTML5, Bootstrap, JavaScript
- **Rich Text**: CKEditor 5
- **Testing**: Django TestCase with 67 tests
- **Deployment**: PythonAnywhere
- **Documentation**: MkDocs Material

## 📚 Documentation

### Development
- **[Development Guide](DEVELOPMENT.md)** - Setup, commands, and workflow
- **[Environment Setup](ENVIRONMENTS.md)** - Local, staging, production configs
- **[Commands Reference](COMMANDS.md)** - Django management commands

### Technical Reference  
- **[Project Architecture](ARCHITECTURE.md)** - Technical overview
- **[Models API](api/models.md)** - Database models
- **[Views API](api/views.md)** - Request handlers
- **[Forms API](api/forms.md)** - Form validation

### Deployment & Operations
- **[Deployment Guide](DEPLOYMENT.md)** - PythonAnywhere deployment
- **[Troubleshooting](TROUBLESHOOTING.md)** - Common issues

### User Guide
- **[Danish User Guide](BRUGERVEJLEDNING.md)** - Admin interface guide (Danish)

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
python scripts/run_tests.py

# Run specific test files  
python manage.py test club_management.tests.test_models
python manage.py test club_management.tests.test_forms
```

**Test Coverage**: 67 tests covering models, forms, views, and core functionality.

## 🌐 Environments

| Environment | Branch | Database | URL | Purpose |
|------------|--------|----------|-----|---------|
| **Local** | feature/* | SQLite | http://localhost:8000 | Development |
| **Staging** | dev/test-site | MySQL | TBD | Testing |
| **Production** | main | MySQL | https://ruder10.pythonanywhere.com | Live site |

## 🎯 Getting Help

- **Development Issues**: See [Troubleshooting Guide](TROUBLESHOOTING.md)
- **Setup Problems**: Check [Development Guide](DEVELOPMENT.md)  
- **Deployment Issues**: See [Deployment Guide](DEPLOYMENT.md)

---

*Built with Django for bridge clubs everywhere* 🃏