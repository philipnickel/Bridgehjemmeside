# Simple developer Makefile for Bridgehjemmeside

SHELL := /bin/bash

# Paths
VENV := .venv
PY := $(VENV)/bin/python
PIP := $(VENV)/bin/pip
PROJECT_DIR := bridge_club_management
MANAGE := $(PY) $(PROJECT_DIR)/manage.py

# Options
PORT ?= 8000
HOST ?= 0.0.0.0

.PHONY: help install migrate makemigrations check run serve createsuperuser shell

help:
	@echo "Useful targets:"
	@echo "  make serve            # Run migrations and start dev server"
	@echo "  make migrate          # Apply database migrations"
	@echo "  make makemigrations   # Create new migrations for model changes"
	@echo "  make check            # Django system checks"
	@echo "  make install          # Install Python deps from requirements.txt"
	@echo "  make createsuperuser  # Create a Django superuser"
	@echo "  make shell            # Django shell with venv"

install:
	@echo "Installing Python dependencies..."
	$(PIP) install -r $(PROJECT_DIR)/requirements.txt

migrate:
	@echo "Applying migrations..."
	$(MANAGE) migrate --noinput

makemigrations:
	@echo "Making migrations (if any changes)..."
	$(MANAGE) makemigrations

check:
	@echo "Running Django system checks..."
	$(MANAGE) check

run:
	@echo "Starting development server at http://$(HOST):$(PORT)/ ..."
	$(MANAGE) runserver $(HOST):$(PORT)

serve: migrate run

createsuperuser:
	$(MANAGE) createsuperuser

shell:
	$(MANAGE) shell

