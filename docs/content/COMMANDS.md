# Commands Reference

Quick reference for common Django and deployment commands.

## 🚀 Development Commands

### Local Development Setup
```bash
# Initial setup
cd bridge_club_management
pip install -r requirements/local.txt
cp .env.template .env

# Database setup
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic

# Run development server
python manage.py runserver
# Opens at: http://127.0.0.1:8000/
```

### Django Management Commands
```bash
# Database operations
python manage.py makemigrations          # Create new migrations
python manage.py migrate                 # Apply migrations
python manage.py showmigrations         # Show migration status

# Data management
python manage.py loaddata fixtures.json # Load fixture data
python manage.py dumpdata app.model     # Export data

# User management
python manage.py createsuperuser        # Create admin user
python manage.py changepassword username # Change user password

# Development utilities
python manage.py check                   # Check for issues
python manage.py shell                   # Django shell
python manage.py dbshell                # Database shell
```

### Custom Management Commands
```bash
# Bridge club specific commands
python manage.py create_days            # Create day records
python manage.py ensure_substitutlister # Ensure substitute lists exist
python manage.py update_day_names       # Update day names
python manage.py update_substitution_lists # Update substitution lists
python manage.py update_weeks           # Update week records
```

## 🌐 Environment Commands

### Local Environment (SQLite)
```bash
export DJANGO_SETTINGS_MODULE=bridge_club_management.settings.local
python manage.py runserver
```

### Development Environment (PythonAnywhere Dev)
```bash
export DJANGO_SETTINGS_MODULE=bridge_club_management.settings.develop
python manage.py migrate
python manage.py collectstatic --noinput
```

### Production Environment (PythonAnywhere Live)
```bash
export DJANGO_SETTINGS_MODULE=bridge_club_management.settings.production
python manage.py migrate
python manage.py collectstatic --noinput
```

## 🚀 Deployment Commands

### PythonAnywhere Deployment
```bash
# SSH into server
ssh Ruder10@ssh.pythonanywhere.com

# Navigate to project
cd /home/Ruder10/Bridgehjemmeside/bridge_club_management

# Pull latest changes
git pull origin develop    # For dev server
git pull origin main       # For production

# Install/update dependencies
pip install --user -r requirements/production.txt

# Apply database changes
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Reload web app (in PythonAnywhere dashboard)
# OR use API call:
# python manage.py reload_webapp Ruder10.pythonanywhere.com
```

### Git Workflow Commands
```bash
# Start new feature
git checkout main
git pull origin main
git checkout -b feature/feature-name

# Work on feature
git add .
git commit -m "Add feature description"
git push origin feature/feature-name

# Deploy to development
git checkout develop
git merge feature/feature-name
git push origin develop

# Deploy to production
git checkout main
git merge develop
git push origin main
```

## 🔧 Maintenance Commands

### Database Backup (Production)
```bash
# Create backup
python manage.py dumpdata > backup_$(date +%Y%m%d_%H%M%S).json

# MySQL backup (on PythonAnywhere)
mysqldump -u Ruder10 -p --databases Ruder10$default > backup.sql
```

### Static Files Management
```bash
# Collect static files
python manage.py collectstatic --noinput

# Clear static files (if needed)
python manage.py collectstatic --clear --noinput
```

### Log Management
```bash
# View recent logs
tail -f debug.log

# View Django logs (production)
tail -f /var/log/Ruder10.pythonanywhere.com.error.log
```

## 🐛 Debugging Commands

### Check Project Health
```bash
python manage.py check                  # Overall system check
python manage.py check --deploy        # Production readiness check
python manage.py validate             # Validate models
```

### Database Debugging
```bash
python manage.py showmigrations       # Show migration status
python manage.py sqlmigrate app 0001  # Show SQL for migration
python manage.py shell                # Interactive shell
```

### Performance Analysis
```bash
python manage.py runserver --settings=settings.local
# Add ?debug=1 to URLs to see debug info
```

## 📦 Package Management

### Requirements Files
```bash
# Install for different environments
pip install -r requirements/local.txt      # Local development
pip install -r requirements/production.txt # Production

# Update requirements
pip freeze > requirements/base.txt
```

### Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate (Linux/Mac)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate

# Deactivate
deactivate
```

## ⚡ Quick Reference

| Task | Command |
|------|---------|
| Start local server | `python manage.py runserver` |
| Apply migrations | `python manage.py migrate` |
| Create admin user | `python manage.py createsuperuser` |
| Check for issues | `python manage.py check` |
| Collect static files | `python manage.py collectstatic` |
| View migrations | `python manage.py showmigrations` |
| Django shell | `python manage.py shell` |

---
*For deployment-specific commands, see [DEPLOYMENT.md](DEPLOYMENT.md)*