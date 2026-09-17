# CBT System

Computer-Based Test system built with Django, Bootstrap 5, and SQLite.

## Setup

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py createsuperuser   # creates the first Super Admin
python manage.py runserver
```

## Status

Phase 2 complete: project config + `accounts` app (custom User model,
role-based auth, Super Admin account management).

Later phases add: `exams` (subjects/questions), `attempts` (exam-taking,
scoring, PDF results), and `core` (role dashboards).
