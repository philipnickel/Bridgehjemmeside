#!/bin/bash

# Deployment script for PythonAnywhere
# Usage: ./scripts/deploy.sh [staging|production]

set -e  # Exit on any error

ENVIRONMENT=${1:-staging}
BRANCH=""
SETTINGS_MODULE=""

# Determine branch and settings based on environment
case $ENVIRONMENT in
    "staging")
        BRANCH="dev"
        SETTINGS_MODULE="bridge_club_management.settings.staging"
        echo "🚀 Deploying to STAGING environment..."
        ;;
    "production")
        BRANCH="main"
        SETTINGS_MODULE="bridge_club_management.settings.production"
        echo "🚀 Deploying to PRODUCTION environment..."
        ;;
    *)
        echo "❌ Invalid environment. Use 'staging' or 'production'"
        exit 1
        ;;
esac

echo "Environment: $ENVIRONMENT"
echo "Branch: $BRANCH"
echo "Settings: $SETTINGS_MODULE"
echo ""

# Backup current deployment (optional)
echo "📦 Creating backup..."
if [ -f "manage.py" ]; then
    cp -r . "../backup-$(date +%Y%m%d-%H%M%S)" || true
fi

# Pull latest code
echo "⬇️  Pulling latest code from $BRANCH..."
git fetch origin
git checkout $BRANCH
git pull origin $BRANCH

# Set environment variables
export DJANGO_SETTINGS_MODULE=$SETTINGS_MODULE

# Navigate to Django project directory
cd bridge_club_management

# Install/update dependencies
echo "📦 Installing dependencies..."
pip install -r requirements/base.txt --user

if [ "$ENVIRONMENT" = "staging" ]; then
    pip install -r requirements/local.txt --user
else
    pip install -r requirements/production.txt --user
fi

# Run migrations
echo "🗄️  Running database migrations..."
python manage.py migrate --noinput

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput --clear

# Run system checks
echo "🔍 Running Django system checks..."
python manage.py check

# Check for missing migrations
echo "🔍 Checking for missing migrations..."
python manage.py makemigrations --check --dry-run

# Restart web app (PythonAnywhere specific)
echo "🔄 Restarting web application..."
if command -v pa_reload_webapp.py &> /dev/null; then
    # This command is available in PythonAnywhere console
    if [ "$ENVIRONMENT" = "staging" ]; then
        pa_reload_webapp.py bridgeclub-dev.pythonanywhere.com || echo "⚠️  Manual restart may be needed"
    else
        pa_reload_webapp.py bridgeclub.pythonanywhere.com || echo "⚠️  Manual restart may be needed"
    fi
else
    echo "⚠️  Please manually restart the web app in PythonAnywhere dashboard"
fi

echo ""
echo "✅ Deployment completed successfully!"
echo "🌐 Check your site to verify everything is working"

if [ "$ENVIRONMENT" = "staging" ]; then
    echo "🔗 Staging URL: https://bridgeclub-dev.pythonanywhere.com"
else
    echo "🔗 Production URL: https://bridgeclub.pythonanywhere.com"
fi 