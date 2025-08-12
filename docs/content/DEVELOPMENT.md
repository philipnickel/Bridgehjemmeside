# Development Guide

Complete development workflow for the Bridge Club Management System.

## 🚀 Quick Setup

### Prerequisites
- Python 3.11
- Conda environment named `bridge`
- Git

### Initial Setup

```bash
# Clone repository
git clone https://github.com/philipnickel/Bridgehjemmeside.git
cd Bridgehjemmeside

# Activate conda environment  
conda activate bridge

# Navigate to Django project
cd bridge_club_management

# Install dependencies
pip install -r requirements/local.txt

# Setup environment file
cp env.template .env

# Initialize database
python manage.py migrate

# Create admin user
python manage.py createsuperuser

# Run development server
python manage.py runserver
```

**Local site**: http://localhost:8000

## 🔧 Common Development Commands

### Django Commands

```bash
# Run development server
python manage.py runserver

# Database operations
python manage.py makemigrations
python manage.py migrate
python manage.py dbshell

# Testing
python scripts/run_tests.py
python manage.py test club_management.tests.test_models

# Admin and data
python manage.py createsuperuser
python manage.py collectstatic
python manage.py shell_plus

# Reset local database (SQLite only)
rm db.sqlite3 && python manage.py migrate
```

### Git Workflow

```bash
# Create feature branch
git checkout dev/test-site
git pull origin dev/test-site
git checkout -b feature/your-feature-name

# Work on feature, then commit
git add .
git commit -m "feat: your feature description"
git push -u origin feature/your-feature-name

# Create pull request to dev/test-site
# After review and testing, merge to main
```

## 🌐 Environments & Deployment

### Local Development
- **Branch**: `feature/*`
- **Database**: SQLite (`db.sqlite3`)
- **Settings**: `bridge_club_management.settings.local`
- **URL**: http://localhost:8000

```bash
export DJANGO_SETTINGS_MODULE=bridge_club_management.settings.local
python manage.py runserver
```

### Staging Environment
- **Branch**: `dev/test-site`
- **Database**: MySQL (PythonAnywhere)
- **Settings**: `bridge_club_management.settings.staging`

### Production Environment  
- **Branch**: `main`
- **Database**: MySQL (PythonAnywhere)
- **Settings**: `bridge_club_management.settings.production`
- **URL**: https://ruder10.pythonanywhere.com

#### Production SSH Access

```bash
# SSH to production server
ssh Ruder10@ssh.pythonanywhere.com

# Navigate to project
cd /home/Ruder10/Bridgehjemmeside/bridge_club_management

# Run Django commands on production
python manage.py migrate --settings=bridge_club_management.settings.production
python manage.py collectstatic --settings=bridge_club_management.settings.production
```

#### Production Database Access

```bash
# Access MySQL console
mysql -u Ruder10 -p -h Ruder10.mysql.pythonanywhere-services.com 'Ruder10$bridge_main'

# Django shell on production
python manage.py shell --settings=bridge_club_management.settings.production
```

## 📝 VS Code Tasks

Open Command Palette (`Cmd+Shift+P`) → "Tasks: Run Task":

- **Django: Run Server (Local)** - Start development server
- **Run Tests (local)** - Run all tests  
- **Docs: Serve Documentation** - Serve docs at http://127.0.0.1:8001
- **Django: Migrate** - Apply database migrations
- **Django: Create Superuser** - Create admin user

## 🧪 Testing

### Run Tests

```bash
# All tests
python scripts/run_tests.py

# Specific test files
python manage.py test club_management.tests.test_models
python manage.py test club_management.tests.test_forms  
python manage.py test club_management.tests.test_views

# With coverage
coverage run --source='.' manage.py test
coverage report
coverage html
```

### Test Structure
- **Location**: `club_management/tests/`
- **Files**: `test_*.py`
- **Coverage**: 67 tests total
- **Framework**: Django TestCase

## 🏗️ Project Structure

### Key Directories

```bash
bridge_club_management/
├── bridge_club_management/     # Project settings
│   └── settings/              # Environment configs
├── club_management/           # Main app
│   ├── models.py             # Database models
│   ├── views.py              # Request handlers
│   ├── forms.py              # Form definitions
│   ├── admin.py              # Admin interface
│   ├── templates/            # HTML templates
│   ├── tests/                # Test files
│   └── management/commands/   # Custom commands
├── requirements/             # Dependencies
├── scripts/                  # Utility scripts
└── static/                   # Static files
```

### Key Models
- **CustomUser** - User management with availability
- **Afmeldingsliste** - Registration lists
- **Substitutliste** - Substitute lists  
- **UserSubstitutAssignment** - Assignment tracking

## 🔄 Development Workflow

1. **Feature Development**
   ```bash
   git checkout -b feature/your-feature
   # Develop locally with SQLite
   python scripts/run_tests.py
   ```

2. **Pull Request Process**
   - Create PR to `dev/test-site`
   - GitHub Actions runs tests automatically
   - Code review required
   - Test on staging after merge

3. **Production Deployment**
   - Create PR from `dev/test-site` to `main`
   - Manual deployment to production
   - Verify on live site

## 📊 Useful Commands

### Database Operations

```bash
# Check migrations
python manage.py showmigrations

# Create migration for schema changes
python manage.py makemigrations club_management

# SQL for migration (dry run)
python manage.py sqlmigrate club_management 0001

# Load data from fixtures
python manage.py loaddata backup.json
```

### Debugging

```bash
# Django shell with models loaded
python manage.py shell_plus

# Show all URLs
python manage.py show_urls

# Django system check
python manage.py check

# Collect static files
python manage.py collectstatic --noinput
```

### Production Utilities

```bash
# Create database backup
python manage.py dumpdata > backup_$(date +%Y%m%d).json

# SSH and check logs
ssh Ruder10@ssh.pythonanywhere.com
tail -f /var/log/Ruder10.pythonanywhere.com.error.log

# Restart web app
# Via PythonAnywhere web console: Web tab → Reload
```

## 🛠️ Environment Variables

Create `.env` file in `bridge_club_management/`:

```bash
# Required for local development
DJANGO_SETTINGS_MODULE=bridge_club_management.settings.local
DJANGO_SECRET_KEY=your-secret-key-here
DEBUG=True

# Optional for email testing
EMAIL_HOST_USER=your-email@example.com
EMAIL_HOST_PASSWORD=your-app-password
```

## 🚨 Troubleshooting

### Common Issues

```bash
# Permission denied on PythonAnywhere
chmod +x manage.py

# Module not found errors
pip install -r requirements/local.txt

# Database locked (SQLite)
rm db.sqlite3 && python manage.py migrate

# Static files not loading
python manage.py collectstatic --clear

# Port already in use
python manage.py runserver 8001
```

### Reset Everything (Local Only)

```bash
# Nuclear reset - delete everything and start fresh
rm db.sqlite3
rm -rf club_management/migrations/00*.py
python manage.py makemigrations club_management
python manage.py migrate
python manage.py createsuperuser
```

---

*For deployment issues, see [Deployment Guide](DEPLOYMENT.md)*  
*For operational issues, see [Troubleshooting Guide](TROUBLESHOOTING.md)*