# Bridge Club Management System

A Django-based web application for managing bridge club activities, substitute lists, and member coordination.

## 🚀 Quick Start

```bash
# Clone and setup
git clone https://github.com/philipnickel/Bridgehjemmeside.git
cd Bridgehjemmeside/bridge_club_management

# Local development
pip install -r requirements/local.txt
cp .env.template .env
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

**Local site:** [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

## 📚 Documentation Overview

=== "User Guides"

    Perfect for development and maintenance tasks:

    - **[Development Workflow](../DEVELOPMENT.md)** - Git workflow, feature development, deployment process
    - **[Environment Setup](ENVIRONMENTS.md)** - Local, development, and production configuration
    - **[Commands Reference](COMMANDS.md)** - Django management commands and deployment commands
    - **[Deployment Guide](DEPLOYMENT.md)** - PythonAnywhere deployment procedures
    - **[Troubleshooting](TROUBLESHOOTING.md)** - Common issues and solutions

=== "Technical Reference"

    Understanding the codebase:

    - **[Project Architecture](ARCHITECTURE.md)** - Technical overview and structure
    - **[Models API](api/models.md)** - Database models and relationships
    - **[Views API](api/views.md)** - Web views and request handling
    - **[Forms API](api/forms.md)** - User input forms and validation
    - **[Admin API](api/admin.md)** - Django admin configuration

=== "User Management"

    For club administrators:

    - **[Danish User Guide](BRUGERVEJLEDNING.md)** - Complete admin interface guide
    - **[Management Commands](api/management.md)** - Automated maintenance tasks

## 🏗️ Project Structure

```
├── bridge_club_management/          # Django project
│   ├── bridge_club_management/      # Project settings
│   │   ├── settings/               # Environment-specific settings
│   │   │   ├── base.py            # Shared settings
│   │   │   ├── local.py           # Local development
│   │   │   ├── develop.py         # Development server
│   │   │   └── production.py      # Production server
│   ├── club_management/            # Main Django app
│   ├── requirements/               # Environment requirements
│   └── static/                     # Static files
├──                           # User guides and documentation
└── mkdocs.yml                     # Documentation configuration
```

## 🌐 Environments

| Environment | Purpose | Database | URL | Status |
|-------------|---------|----------|-----|--------|
| **Local** | Development & Testing | SQLite | http://127.0.0.1:8000/ | ✅ Ready |
| **Development** | Feature Testing | MySQL (Test) | TBD | 🔄 In Progress |
| **Production** | Live Site | MySQL (Prod) | [ruder10.pythonanywhere.com](https://ruder10.pythonanywhere.com) | ✅ Live |

## 🔧 Key Technologies

- **Backend**: Django 4.2.15, Python 3.11
- **Database**: SQLite (local), MySQL (servers)
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap
- **Rich Text**: CKEditor 5
- **Deployment**: PythonAnywhere
- **Documentation**: MkDocs Material
- **Version Control**: Git with feature branch workflow

## 🎯 Key Features

!!! info "Core Functionality"

    - **User Management**: Custom user model with club-specific fields
    - **Substitute Lists**: Automated weekly substitute list generation
    - **Assignment Tracking**: Status management for substitute assignments
    - **Email Notifications**: Automatic coordinator notifications
    - **Admin Interface**: Django admin with custom configurations
    - **Multi-Environment**: Separate local, development, and production setups

## 📞 Support & Contact

- **Documentation Issues**: Check the guides in the navigation above
- **Development Help**: See [Troubleshooting Guide](TROUBLESHOOTING.md)
- **Deployment Issues**: See [Deployment Guide](DEPLOYMENT.md)
- **Questions**: Contact Philip at [Philipnickel@outlook.dk](mailto:Philipnickel@outlook.dk)

## 🚦 Project Status

- ✅ **Multi-environment setup** - Local, development, production configurations
- ✅ **Local development ready** - SQLite database, debug mode, console email
- ✅ **Comprehensive documentation** - User guides and API reference
- ✅ **Professional documentation site** - MkDocs with Material theme
- 🔄 **Development server setup** - In progress on PythonAnywhere
- ⏳ **GitHub Actions CI/CD** - Planned for automated testing and deployment

---

*Last updated: August 2025 • [View on GitHub](https://github.com/philipnickel/Bridgehjemmeside)*