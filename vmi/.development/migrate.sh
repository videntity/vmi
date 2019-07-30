#!/bin/sh

# Create the database tables
python manage.py migrate

# Create a superuser
python manage.py createsuperuser

# Create default groups
python manage.py create_default_groups
