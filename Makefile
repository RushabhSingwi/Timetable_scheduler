# Variables
PYTHON=python
MANAGE=$(PYTHON) manage.py

# Default command: Start the development server
runserver:
	$(MANAGE) runserver

# Run migrations
migrate:
	$(MANAGE) migrate

# Create migration files
makemigrations:
	$(MANAGE) makemigrations

# Collect static files
collectstatic:
	$(MANAGE) collectstatic --noinput

# Start the Django shell
shell:
	$(MANAGE) shell

# Create a superuser
superuser:
	$(MANAGE) createsuperuser

# Install dependencies
install:
	pip install -r requirements.txt

# Run tests
test:
	$(MANAGE) test
