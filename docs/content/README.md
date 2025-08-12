# Bridge Club Management System 🃏

A professional Django-based web application for managing bridge club activities, substitute lists, and member coordination.

## 🚀 Quick Start

```bash
# Clone and setup
git clone https://github.com/philipnickel/Bridgehjemmeside.git
cd Bridgehjemmeside/bridge_club_management

# Install and run locally
pip install -r requirements/local.txt
cp env.template .env
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

**Local site**: http://localhost:8000

## 📚 Complete Documentation

**Full documentation**: [https://philipnickel.github.io/Bridgehjemmeside/](https://philipnickel.github.io/Bridgehjemmeside/)

### Key Documents
- **[Development Guide](DEVELOPMENT.md)** - Setup, commands, SSH access
- **[Project Architecture](ARCHITECTURE.md)** - Technical overview
- **[Deployment Guide](DEPLOYMENT.md)** - PythonAnywhere deployment
- **[API Reference](api/)** - Models, views, forms documentation

## 🔧 Technology Stack

- **Backend**: Django 4.2+, Python 3.11
- **Database**: SQLite (local), MySQL (production)
- **Frontend**: HTML5, Bootstrap, JavaScript, CKEditor 5
- **Testing**: 67 tests with Django TestCase
- **Deployment**: PythonAnywhere (https://ruder10.pythonanywhere.com)
- **Documentation**: MkDocs Material

## 🎯 Key Features

- **Substitute Management**: Automated substitute list generation
- **User Management**: Custom user system with availability tracking
- **Event Registration**: Registration with waitlists and notifications
- **Admin Interface**: Django admin with custom configurations
- **Multi-Environment**: Local, staging, and production setups

## 🧪 Testing

```bash
# Run all 67 tests
python scripts/run_tests.py

# Run specific test modules
python manage.py test club_management.tests.test_models
python manage.py test club_management.tests.test_forms
```

## 🌐 Environments

| Environment | Branch | Database | URL |
|-------------|--------|----------|-----|
| Local | feature/* | SQLite | http://localhost:8000 |
| Staging | dev/test-site | MySQL | TBD |
| Production | main | MySQL | https://ruder10.pythonanywhere.com |

## 🚀 Deployment Access

```bash
# SSH to production server
ssh Ruder10@ssh.pythonanywhere.com

# Navigate to project
cd /home/Ruder10/Bridgehjemmeside/bridge_club_management

# Run production commands
python manage.py migrate --settings=bridge_club_management.settings.production
```

---

*Complete setup instructions, troubleshooting, and API documentation available at [philipnickel.github.io/Bridgehjemmeside](https://philipnickel.github.io/Bridgehjemmeside/)*