#!/bin/sh

# Create the database tables
python manage.py migrate

# Create a superuser
python manage.py createsuperuser
