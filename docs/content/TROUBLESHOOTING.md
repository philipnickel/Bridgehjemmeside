# Troubleshooting Guide

Solutions to common problems you might encounter during development and deployment.

## 🔧 Local Development Issues

### Django Won't Start

**Error**: `ImportError: Couldn't import Django`
```bash
# Solution: Install Django and dependencies
pip install -r requirements/local.txt

# Or install Django directly
pip install Django==4.2.15
```

**Error**: `ModuleNotFoundError: No module named 'bridge_club_management.settings'`
```bash
# Solution: Set Django settings module
export DJANGO_SETTINGS_MODULE=bridge_club_management.settings.local

# Or run with explicit settings
python manage.py runserver --settings=bridge_club_management.settings.local
```

**Error**: `django.core.exceptions.ImproperlyConfigured: The SECRET_KEY setting must not be empty`
```bash
# Solution: Check your environment variables or settings
cp .env.template .env
# Edit .env with proper values

# Or set directly
export DJANGO_SECRET_KEY=your-secret-key-here
```

### Database Issues

**Error**: `django.db.utils.OperationalError: no such table`
```bash
# Solution: Run migrations
python manage.py migrate

# If migrations are corrupted
rm db_local.sqlite3
python manage.py migrate
python manage.py createsuperuser
```

**Error**: `django.db.utils.OperationalError: database is locked`
```bash
# Solution: Close other connections to database
# Check if another runserver is running
ps aux | grep runserver
kill <process_id>

# Or remove lock file
rm db_local.sqlite3-wal
rm db_local.sqlite3-shm
```

**Error**: Migration conflicts
```bash
# Solution: Resolve migration conflicts
python manage.py showmigrations
python manage.py migrate --merge

# If that fails, reset migrations (LOCAL ONLY!)
rm club_management/migrations/00*.py
python manage.py makemigrations club_management
python manage.py migrate
```

### Static Files Not Loading

**Problem**: CSS/JS files not loading in development
```bash
# Solution: Check static files configuration
python manage.py collectstatic

# For development, ensure STATICFILES_DIRS is set
# In settings/local.py:
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]
```

## 🌐 PythonAnywhere Deployment Issues

### SSH Connection Problems

**Error**: `Permission denied (publickey)`
```bash
# Solution: Check SSH key setup
ssh-add -l  # List SSH keys
cat ~/.ssh/id_ed25519.pub  # Copy public key

# Add public key to PythonAnywhere Account → SSH Keys
```

**Error**: `Host key verification failed`
```bash
# Solution: Accept host key
ssh -o StrictHostKeyChecking=no Ruder10@ssh.pythonanywhere.com
# Answer 'yes' when prompted
```

### Web App Not Updating

**Problem**: Changes not visible after deployment
```bash
# Solution 1: Reload web app
# Go to PythonAnywhere Web tab → Click "Reload"

# Solution 2: Check if files were actually updated
ssh Ruder10@ssh.pythonanywhere.com
cd /home/Ruder10/Bridgehjemmeside/bridge_club_management
git status
git log -1  # Check latest commit

# Solution 3: Clear browser cache
# Hard refresh: Ctrl+F5 (Windows) or Cmd+Shift+R (Mac)
```

### Database Connection Errors

**Error**: `django.db.utils.OperationalError: (2003, "Can't connect to MySQL server")`
```bash
# Solution: Check database configuration
ssh Ruder10@ssh.pythonanywhere.com

# Verify environment variables
echo $DB_PASSWORD
echo $DB_NAME
echo $DB_HOST

# Test MySQL connection
mysql -u Ruder10 -p -h Ruder10.mysql.pythonanywhere-services.com
```

**Error**: `django.db.utils.OperationalError: (1045, "Access denied for user")`
```bash
# Solution: Check database credentials
# 1. Verify password in PythonAnywhere Databases tab
# 2. Update environment variable
export DB_PASSWORD='correct-password-here'

# 3. Check database name
export DB_NAME='Ruder10$bridgeclub_dev'  # For development
export DB_NAME='Ruder10$default'         # For production
```

### Module Import Errors

**Error**: `ModuleNotFoundError: No module named 'django_ckeditor_5'`
```bash
# Solution: Install missing packages
ssh Ruder10@ssh.pythonanywhere.com
cd /home/Ruder10/Bridgehjemmeside/bridge_club_management

# Install requirements
pip3.10 install --user -r requirements/production.txt

# Or install specific package
pip3.10 install --user django-ckeditor
```

**Error**: `ImportError: No module named 'MySQLdb'`
```bash
# Solution: Install MySQL client
pip3.10 install --user mysqlclient

# If compilation fails, check if mysqlclient is in requirements
cat requirements/production.txt | grep mysql
```

## 🔀 Git Issues

### Merge Conflicts

**Error**: Git merge conflicts during deployment
```bash
# Solution: Resolve conflicts locally first
git status
git diff

# Edit conflicted files, then:
git add .
git commit -m "Resolve merge conflicts"
git push origin develop  # or main
```

### Pushed Sensitive Data

**Problem**: Accidentally committed passwords or secrets
```bash
# Solution: Remove from history (if recent)
git reset --soft HEAD~1
git reset HEAD
# Edit files to remove sensitive data
git add .
git commit -m "Remove sensitive data"

# If already pushed - contact team immediately
# Consider regenerating secrets/passwords
```

### Branch Issues

**Error**: `Your branch is behind 'origin/develop'`
```bash
# Solution: Pull latest changes
git pull origin develop

# If there are conflicts:
git stash  # Save local changes
git pull origin develop
git stash pop  # Restore local changes
```

## 📧 Email Issues

### Emails Not Sending (Production)

**Problem**: Email notifications not working
```bash
# Solution: Check email configuration
ssh Ruder10@ssh.pythonanywhere.com

# Verify email environment variables
echo $DJANGO_EMAIL_HOST_USER
echo $DJANGO_EMAIL_HOST_PASSWORD

# Test email configuration
python3.10 manage.py shell
>>> from django.core.mail import send_mail
>>> send_mail('Test', 'Test message', 'from@example.com', ['to@example.com'])
```

**Problem**: Gmail authentication errors
```bash
# Solution: Use App Password
# 1. Enable 2FA on Gmail account
# 2. Generate App Password in Google Account settings
# 3. Use App Password instead of regular password

export DJANGO_EMAIL_HOST_PASSWORD='your-app-password-here'
```

## 🎨 Static Files Issues

### CSS/JS Not Loading (Production)

**Problem**: Static files return 404 errors
```bash
# Solution 1: Collect static files
ssh Ruder10@ssh.pythonanywhere.com
cd /home/Ruder10/Bridgehjemmeside/bridge_club_management
python3.10 manage.py collectstatic --noinput

# Solution 2: Check static files mapping
# In PythonAnywhere Web tab:
# URL: /static/
# Directory: /home/Ruder10/Bridgehjemmeside/bridge_club_management/static/
```

**Problem**: Static files mapping incorrect
```bash
# Solution: Verify paths match settings
# In settings/production.py:
STATIC_ROOT = '/home/Ruder10/Bridgehjemmeside/bridge_club_management/static'

# Check if directory exists and has files
ls -la /home/Ruder10/Bridgehjemmeside/bridge_club_management/static/
```

## 🔒 Permission Issues

### File Permission Errors

**Error**: `PermissionError: [Errno 13] Permission denied`
```bash
# Solution: Fix file permissions
chmod +x manage.py
chmod +x scripts/*.sh

# For directories:
chmod 755 /home/Ruder10/Bridgehjemmeside/
```

### Django Admin Access Issues

**Problem**: Can't login to admin interface
```bash
# Solution: Create superuser
python manage.py createsuperuser

# Or check existing users
python manage.py shell
>>> from django.contrib.auth import get_user_model
>>> User = get_user_model()
>>> User.objects.filter(is_superuser=True)
```

## 🐛 Common Django Errors

### Template Not Found

**Error**: `TemplateDoesNotExist`
```bash
# Solution: Check template paths
# In settings/base.py:
TEMPLATES = [{
    'DIRS': [os.path.join(BASE_DIR, 'templates')],
    # ...
}]

# Verify template file exists
ls -la club_management/templates/
```

### URL Pattern Issues

**Error**: `django.urls.exceptions.NoReverseMatch`
```bash
# Solution: Check URL names and patterns
# In templates, ensure URL names match:
{% url 'front_page' %}  # Must match name in urls.py

# Check URL patterns:
python manage.py shell
>>> from django.urls import reverse
>>> reverse('front_page')
```

### Model Field Errors

**Error**: `django.core.exceptions.FieldError`
```bash
# Solution: Check model field names
# Common causes:
# - Field name typos
# - Migrations not applied
# - Model changes without migrations

python manage.py makemigrations
python manage.py migrate
```

## 🔍 Performance Issues

### Slow Page Loading

**Problem**: Pages loading very slowly
```bash
# Solution 1: Check database queries
# Add to settings/local.py:
LOGGING = {
    'version': 1,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}

# Solution 2: Install Django Debug Toolbar
pip install django-debug-toolbar
# Follow setup instructions in docs
```

### Memory Issues (PythonAnywhere)

**Problem**: Process killed due to memory usage
```bash
# Solution: Optimize code and queries
# 1. Use select_related() and prefetch_related()
# 2. Paginate large querysets
# 3. Avoid loading all objects at once

# Example optimization:
# Before:
users = CustomUser.objects.all()

# After:
users = CustomUser.objects.select_related('day').prefetch_related('assignments')[:100]
```

## 📞 Getting Additional Help

### Log Analysis

```bash
# View Django logs
tail -f debug.log

# View error logs (PythonAnywhere)
tail -f /var/log/ruder10.pythonanywhere.com.error.log

# Search for specific errors
grep "ERROR" debug.log | tail -20
```

### Debug Information

```bash
# Check Django configuration
python manage.py check
python manage.py check --deploy

# Check database state
python manage.py showmigrations
python manage.py dbshell

# Environment information
python -c "import django; print(django.get_version())"
python -c "import sys; print(sys.version)"
```

### When to Seek Help

1. **Error persists** after trying solutions above
2. **Data corruption** or loss concerns
3. **Security-related** issues
4. **Production outage** situations

### Contact Information

- **Documentation**: Check other files in `docs/` folder
- **Questions**: Contact Philip at Philipnickel@outlook.dk
- **Emergency**: Production issues need immediate attention

---
*Keep this guide updated as you encounter and solve new issues.*