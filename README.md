# QuizScore Backend

A Django REST Framework API for timed assessments.

## Features
- Server-authoritative scoring (frontend cannot manipulate score)
- Assessment time limits and server-side expiration
- Duplicate final submission prevention
- Detailed scoring breakdown (earned points / total points)
- Automated tests with Pytest

## Setup
1. `python -m venv .venv`
2. `.\.venv\Scripts\Activate.ps1`
3. `pip install -r requirements.txt`
4. `python manage.py migrate`
5. `python manage.py runserver`

## Running Tests
pytest
