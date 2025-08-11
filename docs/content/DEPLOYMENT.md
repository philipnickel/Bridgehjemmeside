# Deployment Guide

Complete guide for deploying the Bridge Club Management System to PythonAnywhere servers.

## 🎯 Deployment Overview

We use a **two-server deployment strategy**:
- **Development Server**: `Ruder10.pythonanywhere.com` (testing)
- **Production Server**: `www.substitutliste.dk` (live site)

## 🚀 Initial Server Setup

### 1. Create Development Server

1. **Log into PythonAnywhere**
2. **Create New Web App**: 
   - Click "Add a new web app"
   - Choose subdomain: `ruder10-dev.pythonanywhere.com`
   - Select Python version: 3.10
   - Choose "Manual configuration"

3. **Configure Web App**:
   - Source code: `/home/Ruder10/Bridgehjemmeside-dev/`
   - Working directory: `/home/Ruder10/Bridgehjemmeside-dev/bridge_club_management/`
   - WSGI file: Edit to point to your Django app

### 2. Setup SSH Access

```bash
# Generate SSH key (if needed)
ssh-keygen -t ed25519

# Copy public key
cat ~/.ssh/id_ed25519.pub

# Add to PythonAnywhere Account → SSH Keys
```

### 3. Clone Repository on Server

```bash
# SSH to server
ssh Ruder10@ssh.pythonanywhere.com

# Clone repository
cd /home/Ruder10/
git clone <your-repo-url> Bridgehjemmeside-dev

# Set up for develop branch
cd Bridgehjemmeside-dev
git checkout develop
```

## 🛠️ Development Server Deployment

### First-Time Setup

```bash
# SSH to development server
ssh Ruder10@ssh.pythonanywhere.com

# Navigate to project
cd /home/Ruder10/Bridgehjemmeside-dev/bridge_club_management

# Set Django settings
export DJANGO_SETTINGS_MODULE=bridge_club_management.settings.develop

# Install dependencies
pip3.10 install --user -r requirements/production.txt

# Setup database
python3.10 manage.py migrate
python3.10 manage.py collectstatic --noinput

# Create superuser
python3.10 manage.py createsuperuser
```

### Configure WSGI File

Edit `/var/www/ruder10_dev_pythonanywhere_com_wsgi.py`:

```python
import os
import sys

# Add project directory to path
path = '/home/Ruder10/Bridgehjemmeside-dev/bridge_club_management'
if path not in sys.path:
    sys.path.append(path)

# Set Django settings module
os.environ['DJANGO_SETTINGS_MODULE'] = 'bridge_club_management.settings.develop'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

### Environment Variables (Development Server)

In PythonAnywhere **Files** tab, create `/home/Ruder10/.bashrc`:

```bash
# Development environment variables
export DJANGO_SECRET_KEY='your-dev-secret-key'
export DB_PASSWORD='your-dev-database-password'
export DB_NAME='Ruder10$bridgeclub_dev'
export DB_USER='Ruder10'
export DB_HOST='Ruder10.mysql.pythonanywhere-services.com'
```

### Regular Deployment (Development)

```bash
# SSH to server
ssh Ruder10@ssh.pythonanywhere.com

# Navigate to project
cd /home/Ruder10/Bridgehjemmeside-dev/bridge_club_management

# Pull latest changes
git pull origin develop

# Install any new dependencies
pip3.10 install --user -r requirements/production.txt

# Apply database changes
python3.10 manage.py migrate

# Collect static files
python3.10 manage.py collectstatic --noinput

# Reload web app (via dashboard or API)
```

## 🏭 Production Server Deployment

### Configure Production WSGI

Edit `/var/www/ruder10_pythonanywhere_com_wsgi.py`:

```python
import os
import sys

# Add project directory to path
path = '/home/Ruder10/Bridgehjemmeside/bridge_club_management'
if path not in sys.path:
    sys.path.append(path)

# Set Django settings module
os.environ['DJANGO_SETTINGS_MODULE'] = 'bridge_club_management.settings.production'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

### Environment Variables (Production)

In PythonAnywhere **Files** tab, edit `/home/Ruder10/.bashrc`:

```bash
# Production environment variables
export DJANGO_SECRET_KEY='your-production-secret-key'
export DB_PASSWORD='your-production-database-password'
export DB_NAME='Ruder10$default'
export DB_USER='Ruder10'
export DB_HOST='Ruder10.mysql.pythonanywhere-services.com'

# Email settings
export DJANGO_EMAIL_HOST_USER='your-email@gmail.com'
export DJANGO_EMAIL_HOST_PASSWORD='your-app-password'
```

### Production Deployment Process

```bash
# SSH to production server
ssh Ruder10@ssh.pythonanywhere.com

# Navigate to production directory
cd /home/Ruder10/Bridgehjemmeside/bridge_club_management

# Create backup before deployment
python3.10 manage.py dumpdata > backup_$(date +%Y%m%d_%H%M%S).json

# Pull latest changes from main branch
git pull origin main

# Install dependencies
pip3.10 install --user -r requirements/production.txt

# Apply migrations
python3.10 manage.py migrate

# Collect static files
python3.10 manage.py collectstatic --noinput

# Reload production web app
# (Do this via PythonAnywhere dashboard)
```

## 🗄️ Database Setup

### Create Development Database

1. **PythonAnywhere Dashboard** → **Databases**
2. **Create Database**: `Ruder10$bridgeclub_dev`
3. **Note password** for environment variables

### Database Migration

```bash
# First-time setup
python3.10 manage.py migrate

# Regular migrations
python3.10 manage.py showmigrations  # Check status
python3.10 manage.py migrate         # Apply new migrations

# If migration conflicts
python3.10 manage.py migrate --merge
```

## 📁 Static Files Configuration

### Development Server Static Files

In PythonAnywhere **Web** tab for dev app:
- **Static files mapping**:
  - URL: `/static/`
  - Directory: `/home/Ruder10/Bridgehjemmeside-dev/bridge_club_management/static/`

### Production Server Static Files

In PythonAnywhere **Web** tab for production app:
- **Static files mapping**:
  - URL: `/static/`
  - Directory: `/home/Ruder10/Bridgehjemmeside/bridge_club_management/static/`

### Collect Static Files

```bash
# Always run after code updates
python3.10 manage.py collectstatic --noinput

# Clear and recollect (if needed)
python3.10 manage.py collectstatic --clear --noinput
```

## 🔄 Automated Deployment (Future)

### GitHub Actions Setup

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to PythonAnywhere

on:
  push:
    branches: [ develop, main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Deploy to Development
      if: github.ref == 'refs/heads/develop'
      run: |
        # SSH and deploy to dev server
        
    - name: Deploy to Production  
      if: github.ref == 'refs/heads/main'
      run: |
        # SSH and deploy to production server
```

## 🚨 Rollback Procedures

### Quick Rollback

```bash
# SSH to affected server
ssh Ruder10@ssh.pythonanywhere.com

# Go to last known good commit
git log --oneline -10  # Find last good commit
git reset --hard <commit-hash>

# Restore database (if needed)
python3.10 manage.py loaddata backup_YYYYMMDD_HHMMSS.json

# Reload web app
```

### Database Rollback

```bash
# Restore from backup
python3.10 manage.py loaddata backup_YYYYMMDD_HHMMSS.json

# Or MySQL restore (if using SQL backup)
mysql -u Ruder10 -p Ruder10$default < backup.sql
```

## 🔍 Health Checks

### Post-Deployment Verification

```bash
# Check Django configuration
python3.10 manage.py check

# Production readiness check
python3.10 manage.py check --deploy

# Test database connection
python3.10 manage.py dbshell

# Verify migrations
python3.10 manage.py showmigrations

# Test admin access
# Visit /admin/ and login
```

### Monitoring

```bash
# View error logs
tail -f /var/log/ruder10.pythonanywhere.com.error.log

# View access logs
tail -f /var/log/ruder10.pythonanywhere.com.access.log

# Django debug log
tail -f ~/Bridgehjemmeside/bridge_club_management/debug.log
```

## 🛡️ Security Checklist

### Pre-Production Deployment

- [ ] Environment variables set correctly
- [ ] SECRET_KEY is unique for production
- [ ] DEBUG = False in production
- [ ] Database password is secure
- [ ] HTTPS configuration (if applicable)
- [ ] Static files collected
- [ ] Email configuration tested
- [ ] Admin user created
- [ ] Backup created

### Post-Deployment

- [ ] Site loads correctly
- [ ] Admin panel accessible
- [ ] Email functionality works
- [ ] Database queries working
- [ ] Static files loading
- [ ] No debug information visible
- [ ] Error pages working (404, 500)

## 🚨 Troubleshooting

### Common Deployment Issues

**"Module not found" errors**
```bash
pip3.10 install --user -r requirements/production.txt
```

**Static files not loading**
```bash
python3.10 manage.py collectstatic --noinput
# Check static files mapping in web app config
```

**Database connection errors**
```bash
# Check environment variables
echo $DB_PASSWORD
echo $DJANGO_SETTINGS_MODULE

# Test database connection
python3.10 manage.py dbshell
```

**Web app not updating**
- Click "Reload" button in PythonAnywhere web tab
- Wait 30-60 seconds for changes to take effect

**Permission errors**
```bash
chmod +x deploy_scripts/*.sh
```

### Log Analysis

```bash
# Check Django logs
tail -f debug.log

# Check web server logs
tail -f /var/log/ruder10.pythonanywhere.com.error.log

# Check specific errors
grep "ERROR" debug.log | tail -20
```

## 📋 Deployment Checklist

### Before Every Deployment

- [ ] Code tested locally
- [ ] All tests passing
- [ ] Migrations created and tested
- [ ] Requirements updated
- [ ] Environment variables configured
- [ ] Backup created

### Development Server Deployment

- [ ] Pull develop branch
- [ ] Install/update dependencies
- [ ] Apply migrations
- [ ] Collect static files
- [ ] Test functionality
- [ ] Notify team

### Production Deployment

- [ ] All development testing complete
- [ ] Create database backup
- [ ] Pull main branch
- [ ] Install/update dependencies
- [ ] Apply migrations
- [ ] Collect static files
- [ ] Reload web app
- [ ] Verify site functionality
- [ ] Monitor for errors

---
*For environment-specific configuration, see [ENVIRONMENTS.md](ENVIRONMENTS.md)*