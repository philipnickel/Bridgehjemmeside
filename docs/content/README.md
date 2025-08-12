# Bridge Club Management System 🃏

A professional Django-based management system for bridge clubs, featuring substitute lists, registration management, and automated workflows.

## 🚀 Quick Start

### Local Development
```bash
# Clone and setup
git clone <repository-url>
cd Bridgehjemmeside
conda activate bridge

# Install dependencies and setup
cd bridge_club_management
pip install -r requirements/local.txt
cp env.template .env

# Run with local settings
export DJANGO_SETTINGS_MODULE=bridge_club_management.settings.local
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

### Access Points
- **Local**: http://localhost:8000
- **Staging**: https://bridgeclub-dev.pythonanywhere.com (dev branch)
- **Production**: https://bridgeclub.pythonanywhere.com (main branch)

## 🏗️ Architecture

### Environment Strategy
- **main** → Production (MySQL on PythonAnywhere)
- **dev** → Staging (MySQL on PythonAnywhere) 
- **feature/*** → Local Development (SQLite)

### Development Workflow
```
feature/your-feature ← Local development with SQLite
↓ (PR review & tests pass)
dev ← Staging with MySQL on PythonAnywhere
↓ (Tested on staging)
main ← Production with MySQL on PythonAnywhere
```

## 🧪 Testing

We maintain comprehensive test coverage:
- **35 tests** covering models, forms, and core functionality
- **GitHub Actions** for automated CI/CD
- **Multiple environments** tested

```bash
# Run tests locally
export DJANGO_SETTINGS_MODULE=bridge_club_management.settings.local
python manage.py test

# Run specific test suites
python manage.py test club_management.tests.test_models
python manage.py test club_management.tests.test_forms
```

## 📚 Documentation

- **[DEVELOPMENT.md](DEVELOPMENT.md)** - Complete development workflow guide
- **[docs/](docs/)** - Technical documentation
- **[bridge_club_management/env.template](bridge_club_management/env.template)** - Environment variables template

## 🛠️ Technology Stack

- **Backend**: Django 4.1+, Python 3.11
- **Database**: SQLite (local), MySQL (staging/production)
- **Frontend**: Bootstrap, Django Templates
- **Deployment**: PythonAnywhere
- **CI/CD**: GitHub Actions
- **Environment**: Conda (`bridge` environment)

## 🎯 Features

- **Substitute Management**: Automated substitute list generation
- **Registration System**: Event registration with waiting lists
- **User Management**: Custom user system with availability tracking
- **Multi-environment**: Professional development workflow
- **Automated Testing**: Comprehensive test suite
- **Documentation**: Complete setup and API documentation

## 🚀 Deployment

### Staging (dev branch)
```bash
./scripts/deploy.sh staging
```

### Production (main branch)
```bash
./scripts/deploy.sh production
```

## 📝 Contributing

1. Create feature branch from `dev`
2. Develop locally with SQLite
3. Write tests for new features
4. Create PR to `dev` (tests must pass)
5. Test on staging environment
6. Create PR from `dev` to `main` for production

## 🔧 Environment Configuration

Each environment has specific settings:

| Environment | Branch | Database | Settings Module | Debug |
|-------------|--------|----------|-----------------|-------|
| Local | feature/* | SQLite | `settings.local` | True |
| Staging | dev | MySQL | `settings.staging` | True |
| Production | main | MySQL | `settings.production` | False |

## 🏆 Project Status

- ✅ **Live Site**: Fully operational
- ✅ **Testing**: 35 tests passing
- ✅ **CI/CD**: GitHub Actions configured
- ✅ **Documentation**: Complete
- ✅ **Multi-environment**: Configured

---

*Built with ❤️ for bridge clubs everywhere*
