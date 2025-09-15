# Bridge Club Management System 🃏

A professional Django-based management system for bridge clubs.

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

## 🛠 Makefile

Common workflows are available via the Makefile at the repo root:

```bash
make help           # list targets
make server         # run dev server
make test           # run tests
make migrate        # apply migrations
```

---
