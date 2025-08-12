# Bridge Club Management System - Development Workflow

## Overview

This project uses a structured development workflow with multiple environments:

- **main**: Production environment on PythonAnywhere (live site)
- **dev**: Staging environment on PythonAnywhere (test site) 
- **feature/***: Local development branches for new features

## Environment Setup

### Local Development (Feature Branches)

1. **Prerequisites:**
   - Python 3.11
   - Conda environment named `bridge` [[memory:5819627]]
   - Git

2. **Initial Setup:**
   ```bash
   # Clone the repository
   git clone <repository-url>
   cd Bridgehjemmeside
   
   # Activate conda environment
   conda activate bridge
   
   # Install dependencies
   cd bridge_club_management
   pip install -r requirements/local.txt
   
   # Copy environment template
   cp env.template .env
   # Edit .env with your local settings
   
   # Run initial migrations
   export DJANGO_SETTINGS_MODULE=bridge_club_management.settings.local
   python manage.py migrate
   
   # Create superuser
   python manage.py createsuperuser
   
   # Load sample data (optional)
   python manage.py loaddata <backup_file>.json
   
   # Run development server
   python manage.py runserver
   ```

3. **Environment Variables (.env):**
   ```bash
   DJANGO_SETTINGS_MODULE=bridge_club_management.settings.local
   DJANGO_SECRET_KEY=your-local-secret-key
   DEBUG=True
   ```

### Staging Environment (dev branch)

- **URL**: `bridgeclub-dev.pythonanywhere.com` (replace with actual)
- **Database**: MySQL on PythonAnywhere (`bridgeclub$bridge_dev`)
- **Settings**: `bridge_club_management.settings.staging`

### Production Environment (main branch)

- **URL**: `bridgeclub.pythonanywhere.com` (replace with actual)
- **Database**: MySQL on PythonAnywhere (`bridgeclub$bridge_main`) [[memory:5835904]]
- **Settings**: `bridge_club_management.settings.production`

## Development Workflow

### Feature Development

1. **Create Feature Branch:**
   ```bash
   git checkout dev
   git pull origin dev
   git checkout -b feature/your-feature-name
   ```

2. **Local Development:**
   - Use SQLite database for local testing
   - Settings automatically configured via `local.py`
   - Run tests: `python manage.py test`

3. **Testing:**
   ```bash
   # Run all tests
   python manage.py test
   
   # Run specific test files
   python manage.py test club_management.tests.test_models
   python manage.py test club_management.tests.test_forms
   
   # Run with coverage
   coverage run --source='.' manage.py test
   coverage report
   ```

### Git Workflow

1. **Feature Development:**
   ```bash
   feature/your-feature ← Local development with SQLite
   ↓ (PR review & tests pass)
   dev ← Staging with MySQL on PythonAnywhere
   ↓ (Tested on staging)
   main ← Production with MySQL on PythonAnywhere
   ```

2. **Pull Request Process:**
   - Create PR from `feature/your-feature` to `dev`
   - GitHub Actions automatically run tests
   - Code review required
   - Merge to `dev` triggers staging deployment
   - Test on staging environment
   - Create PR from `dev` to `main` for production

### Database Management

#### Local Development
- **Database**: SQLite (`db.sqlite3`)
- **Migrations**: `python manage.py migrate`
- **Reset database**: Delete `db.sqlite3` and re-run migrations

#### Loading Production Data Locally
```bash
# Option 1: Load from JSON backup
python manage.py loaddata live_data_backup.json

# Option 2: Import from MySQL dump
# (You'll need to convert MySQL dump to Django fixtures)
```

#### Creating Backups
```bash
# Create JSON backup
python manage.py dumpdata > backup_$(date +%Y%m%d).json

# Exclude certain tables if needed
python manage.py dumpdata --exclude=contenttypes --exclude=auth.permission > backup.json
```

## GitHub Actions CI/CD

### Automated Testing
- Triggers on pushes to `main`, `dev`, `develop`
- Runs on Python 3.11
- Tests with SQLite (local settings)
- Runs full test suite
- Checks for missing migrations
- Validates static file collection

### Test Requirements
- All tests must pass before merge
- No missing migrations
- Static files must collect successfully
- Django system checks must pass

## Development Commands

### Django Management Commands
```bash
# Run development server
python manage.py runserver

# Create and apply migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic

# Run shell with all models loaded
python manage.py shell_plus  # (requires django-extensions)

# Run tests
python manage.py test --verbosity=2
```

### Useful Development Tools
```bash
# Django Debug Toolbar (enabled in local.py)
# Provides SQL query analysis, template debugging, etc.

# Django Extensions
python manage.py shell_plus     # Enhanced shell
python manage.py show_urls      # List all URLs
python manage.py graph_models   # Generate model diagrams
```

## Code Quality

### Testing Guidelines
- Write tests for all new features
- Test both models and forms
- Use meaningful test names and docstrings
- Test edge cases and error conditions

### Best Practices
- Follow Django conventions
- Use environment-specific settings
- Keep sensitive data in environment variables
- Write clear commit messages
- Document complex functionality

## Troubleshooting

### Common Issues

1. **Database Connection Error:**
   - Check `DJANGO_SETTINGS_MODULE` environment variable
   - Verify database settings in appropriate settings file

2. **Migration Issues:**
   ```bash
   # Reset migrations (local only!)
   rm club_management/migrations/00*.py
   python manage.py makemigrations club_management
   python manage.py migrate
   ```

3. **Static Files Not Loading:**
   ```bash
   python manage.py collectstatic --clear
   ```

4. **Import Errors:**
   - Activate correct conda environment: `conda activate bridge`
   - Check all dependencies installed: `pip install -r requirements/local.txt`

### Environment-Specific Settings

Each environment uses different settings:
- **Local**: `bridge_club_management.settings.local` (SQLite, DEBUG=True)
- **Staging**: `bridge_club_management.settings.staging` (MySQL, DEBUG=True)
- **Production**: `bridge_club_management.settings.production` (MySQL, DEBUG=False)

Set via environment variable:
```bash
export DJANGO_SETTINGS_MODULE=bridge_club_management.settings.local
```

## Deployment

### PythonAnywhere Deployment
1. **Staging** (`dev` branch): Automatic deployment to dev environment
2. **Production** (`main` branch): Manual deployment after staging validation

### Environment Variables on PythonAnywhere
Required environment variables:
- `DJANGO_SECRET_KEY`
- `DB_PASSWORD` 
- `DB_NAME`, `DB_USER`, `DB_HOST` (if different from defaults)
- `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD` (if email configured) 