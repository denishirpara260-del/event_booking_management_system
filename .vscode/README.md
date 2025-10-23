Event Management & Ticketing Platform


A Django-based Event Management System for event listing, ticket booking, and user management, including a RESTful API and advanced booking logic.

Backend: Python 3.x, Django 5.x, Django REST Framework

Database: SQLite for development

Frontend: HTML, CSS, JavaScript (minimal, focus on functionality)

Version Control: Git

Rationale: PostgreSQL recommended for production due to robust transactional support and concurrency handling.


1) Code Quality & Security:--

Code Style: Follows PEP 8, with clear and descriptive variable and function names

Security:

CSRF protection enabled for all forms

Passwords hashed with Django’s built-in system

Authentication checks for profile and booking access

DRF endpoints protected via token-based authentication

2)  Setup Instructions:--

Python 3.12+

pip package manager

SQLite

3)  Installation:--

cd event-management

create and activate virtual environment :--

python -m venv venv

venv\Scripts\activate

4)  Install Dependancy:-- 

pip install -r requirements.txt

5)  Apply Migrations:--

python manage.py migrate

6)  create a superuser:--

python manage.py createsuperuser

7)  run the server:--

python manage.py runserver

8)  Features:--

List all the features your project supports:

Event listing (with search and filter)

Event detail view (with ticket types)

User registration, login, logout, and profile page

Ticket booking with atomic transactions

REST API endpoints for events and ticket booking

Management command to purge old events