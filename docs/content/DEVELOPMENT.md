# Development Workflow

Complete guide to the development process, from feature creation to production deployment.

## 🎯 Overview

Our development workflow follows a **three-environment approach** with automated quality control:

```
Local Dev → Development Server → Production
    ↓              ↓                ↓
feature/*      develop branch    main branch
SQLite         MySQL Test        MySQL Prod
```

## 🌟 Git Workflow

### Branch Structure
- **`main`** - Production branch (protected)
- **`develop`** - Development server branch
- **`feature/*`** - Feature development branches
- **`hotfix/*`** - Emergency production fixes

### Starting New Features

```bash
# 1. Start from develop branch
git checkout develop
git pull origin develop

# 2. Create feature branch
git checkout -b feature/user-authentication

# 3. Develop locally
python manage.py runserver
# Work, test, commit

# 4. Push feature branch
git add .
git commit -m "Add user authentication system"
git push origin feature/user-authentication
```

### Feature to Development Server

```bash
# 1. Create Pull Request
# feature/user-authentication → develop

# 2. Code Review
# - Automated checks run (linting, tests)
# - Manual review required
# - Must pass all checks

# 3. Merge to develop
# - Triggers automatic deployment to dev server
# - Development site updates automatically
```

### Development to Production

```bash
# 1. Create Pull Request
# develop → main

# 2. Production Review
# - All previous checks + production-specific tests
# - Manual approval required
# - Database migration validation

# 3. Deploy to Production
# - Manual approval triggers deployment
# - Production site updates
# - Rollback available if needed
```

## 🏗️ Local Development

### Initial Setup
```bash
# Clone repository
git clone <repository-url>
cd Bridgehjemmeside/bridge_club_management

# Install dependencies
pip install -r requirements/local.txt

# Environment setup
cp .env.template .env
# Edit .env with your settings

# Database setup
python manage.py migrate
python manage.py createsuperuser

# Run development server
python manage.py runserver
```

### Daily Development
```bash
# Start development
cd bridge_club_management
python manage.py runserver
# Visit: http://127.0.0.1:8000/

# Apply migrations (when models change)
python manage.py makemigrations
python manage.py migrate

# Update static files (if CSS/JS changes)
python manage.py collectstatic
```

### Testing Your Changes
```bash
# Run basic checks
python manage.py check

# Test migrations
python manage.py migrate --dry-run

# Check for potential issues
python manage.py validate
```

## 🚀 Deployment Process

### Development Server Deployment
**Automatic** when code is pushed to `develop` branch:

1. GitHub Actions runs tests
2. If tests pass → SSH to dev server
3. Pull latest code
4. Run migrations
5. Collect static files
6. Reload web app
7. Notify team via Slack/email

### Production Deployment
**Manual approval** required for `main` branch:

1. All development checks pass
2. Manual code review
3. Production readiness checks
4. **Manual approval** by maintainer
5. Create database backup
6. Deploy to production
7. Health checks
8. Notify team

## 🤖 Automated Quality Control

### On Every Feature Branch Push
- **Code Style**: Black, flake8, isort
- **Type Checking**: mypy (if configured)
- **Security**: bandit security scanning
- **Django Checks**: `manage.py check`
- **Unit Tests**: pytest (if tests exist)

### On Develop Branch
- All feature checks +
- **Integration Tests**: Test with dev database
- **Migration Testing**: Dry-run migrations
- **Performance Tests**: Basic performance checks
- **Automatic Deployment**: To development server

### On Main Branch (Production)
- All previous checks +
- **Production Config Validation**
- **Database Backup**: Automatic before deploy
- **Manual Approval**: Required for deployment
- **Health Checks**: Post-deployment verification
- **Rollback Capability**: Quick revert if needed

## 📊 Code Review Guidelines

### For Reviewers
- ✅ **Functionality**: Does it work as intended?
- ✅ **Security**: No sensitive data exposed?
- ✅ **Performance**: Efficient database queries?
- ✅ **Maintainability**: Clean, readable code?
- ✅ **Tests**: Adequate test coverage?
- ✅ **Documentation**: Updated if needed?

### For Developers
- 📝 **Clear Commits**: Descriptive commit messages
- 🧪 **Test Changes**: Verify functionality works
- 📖 **Update Docs**: Keep documentation current
- 🔒 **Security**: No hardcoded secrets/passwords
- 🎨 **Code Style**: Follow project conventions

## 🛠️ Environment-Specific Development

### Local Development Features
```bash
# Local settings active
DJANGO_SETTINGS_MODULE=bridge_club_management.settings.local

# Features:
- SQLite database (db_local.sqlite3)
- Debug mode enabled
- Console email backend
- Django Debug Toolbar (if installed)
- Hot reload on file changes
```

### Development Server Features
```bash
# Development settings active  
DJANGO_SETTINGS_MODULE=bridge_club_management.settings.develop

# Features:
- MySQL test database
- Debug mode enabled
- Console email backend
- Real server environment testing
- Shared testing with team
```

### Production Features
```bash
# Production settings active
DJANGO_SETTINGS_MODULE=bridge_club_management.settings.production

# Features:
- MySQL production database
- Debug mode disabled
- SMTP email backend
- Security headers enabled
- Performance optimizations
```

## 🚨 Emergency Procedures

### Hotfixes (Production Issues)
```bash
# 1. Create hotfix branch from main
git checkout main
git pull origin main
git checkout -b hotfix/critical-security-fix

# 2. Make minimal fix
# Fix only the critical issue

# 3. Fast-track to production
# Create PR: hotfix/critical-security-fix → main
# Skip development server testing (emergency only)
# Require urgent approval
# Deploy immediately

# 4. Merge back to develop
git checkout develop
git merge hotfix/critical-security-fix
git push origin develop
```

### Rollback Procedure
```bash
# If production deployment fails:
# 1. Immediate rollback to previous version
# 2. Restore database backup (if needed)
# 3. Notify team
# 4. Investigate and fix issues
# 5. Redeploy when ready
```

## 📈 Best Practices

### Commit Messages
```bash
# Good commit messages:
git commit -m "Add user authentication system

- Implement login/logout functionality
- Add password reset feature
- Include email verification
- Add tests for auth views"

# Poor commit messages:
git commit -m "fixes"
git commit -m "update stuff"
```

### Feature Branch Naming
```bash
# Good branch names:
feature/user-authentication
feature/email-notifications
feature/admin-dashboard-improvements
hotfix/security-vulnerability-fix

# Poor branch names:
my-changes
fix
update
test123
```

### Database Changes
```bash
# Always create migrations
python manage.py makemigrations

# Test migrations locally
python manage.py migrate

# Check migration SQL (if complex)
python manage.py sqlmigrate app_name 0001

# Never edit existing migrations
# Create new migration instead
```

## 📞 Getting Help

- **Documentation Issues**: Check the documentation homepage
- **Development Problems**: See [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- **Deployment Issues**: See [DEPLOYMENT.md](DEPLOYMENT.md)
- **Code Questions**: Create GitHub issue or contact team

---
*This workflow ensures code quality, prevents production issues, and enables confident rapid development.*