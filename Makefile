SHELL := /bin/bash
.ONESHELL:

# Minimal Makefile for local development with auto-venv

# Configuration
PROJECT_DIR := bridge_club_management
VENV := .venv
PY := $(CURDIR)/$(VENV)/bin/python
PIP := $(CURDIR)/$(VENV)/bin/pip
PORT := 8010
export DJANGO_SETTINGS_MODULE := bridge_club_management.settings.local

.PHONY: run venv shell

# Run server on port 8010; auto-create .venv and install deps; kill existing process on the port
run:
	set -e
	# Ensure venv exists in repo root (do NOT create a new one if present)
	if [ ! -x "$(PY)" ]; then
	  echo "Creating virtualenv at $(VENV)..."
	  (command -v python3 >/dev/null 2>&1 && python3 -m venv $(VENV)) || python -m venv $(VENV)
	fi
	# Activate the venv for this run
	source $(VENV)/bin/activate
	# Ensure latest Wagtail per requirement
	pip install -q --upgrade "wagtail>=7.1,<8.0"
	# Install dependencies once (with fallback if mysqlclient fails)
	if [ ! -f "$(VENV)/.deps-installed" ]; then
	  echo "Upgrading pip..."
	  pip install --upgrade pip setuptools wheel >/dev/null
	  echo "Installing requirements (base + local)..."
	  if pip install -r $(PROJECT_DIR)/requirements/base.txt -r $(PROJECT_DIR)/requirements/local.txt; then
	    touch $(VENV)/.deps-installed
	  else
	    echo
	    echo "mysqlclient build failed. Retrying without mysqlclient for local SQLite..."
	    TMP_REQ=$$(mktemp)
	    sed '/^mysqlclient.*/d' $(PROJECT_DIR)/requirements/base.txt > $$TMP_REQ
	    sed '/^-r[[:space:]]*base.txt[[:space:]]*$$/d' $(PROJECT_DIR)/requirements/local.txt >> $$TMP_REQ
	    pip install -r $$TMP_REQ && touch $(VENV)/.deps-installed || true
	    rm -f $$TMP_REQ
	  fi
	fi
	# Kill existing process on PORT, if any
	PID=$$(lsof -ti :$(PORT) 2>/dev/null || true)
	if [ -n "$$PID" ]; then
	  echo "Killing process $$PID on port $(PORT)..."
	  kill $$PID || true
	  sleep 1
	fi
	# Create and apply migrations, seed pages, then run server
	python $(PROJECT_DIR)/manage.py makemigrations --noinput
	python $(PROJECT_DIR)/manage.py migrate --noinput
	python $(PROJECT_DIR)/manage.py seed_wagtail_pages || true
	python $(PROJECT_DIR)/manage.py runserver 127.0.0.1:$(PORT)

# Create/refresh the virtualenv and install deps (no server)
venv:
	set -e
	if [ ! -x "$(PY)" ]; then
	  echo "Creating virtualenv at $(VENV)..."
	  (command -v python3 >/dev/null 2>&1 && python3 -m venv $(VENV)) || python -m venv $(VENV)
	fi
	source $(VENV)/bin/activate
	pip install --upgrade pip setuptools wheel
	if pip install -r $(PROJECT_DIR)/requirements/base.txt -r $(PROJECT_DIR)/requirements/local.txt; then
	  touch $(VENV)/.deps-installed
	else
	  echo
	  echo "mysqlclient build failed. Retrying without mysqlclient for local SQLite..."
	  TMP_REQ=$$(mktemp)
	  sed '/^mysqlclient.*/d' $(PROJECT_DIR)/requirements/base.txt > $$TMP_REQ
	  sed '/^-r[[:space:]]*base.txt[[:space:]]*$$/d' $(PROJECT_DIR)/requirements/local.txt >> $$TMP_REQ
	  pip install -r $$TMP_REQ && touch $(VENV)/.deps-installed || true
	  rm -f $$TMP_REQ
	fi

# Open a shell with the repo venv activated
shell:
	@if [ ! -x "$(PY)" ]; then echo "Virtualenv $(VENV) not found. Run: make venv"; exit 1; fi
	@echo "Activating $(VENV). Type 'exit' to leave."
	bash -lc 'source $(VENV)/bin/activate; exec $$SHELL'
