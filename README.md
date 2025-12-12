# NEURO PREDICT

A secure, server-rendered Flask web application to record and manage patient demographics and clinical assessment data and to provide stroke risk assessments. The system enforces role-based access (Super Admin, Doctor, Nurse) and uses a dual-database strategy to balance transactional integrity and flexible clinical documents.

## Features

- Secure session-based authentication (Werkzeug password hashing)
- Patient demographic management and emergency contacts
- MongoDB-backed clinical assessment documents
- Admin user management dashboard (CRUD)
- Role-aware dashboard for clinicians (server-side UI hiding)
- Server-side HTML POST forms with manual CSRF tokens
- Tailwind CSS responsive UI (prebuilt CSS included)
- Database seed script and unit tests (test.py)

## System Architecture

The application follows a three-layer architecture aligned with secure SDLC principles.

| Layer | Responsibility |
|-------|----------------|
| Presentation Layer | Jinja2 templates, server-rendered HTML forms, static assets (Tailwind CSS) |
| Application Layer | Flask backend: routing, authentication, RBAC decorators, business logic |
| Data Layer | SQLite for relational auth/patient registry; MongoDB for flexible assessment documents |

## Tech Stack

| Category | Technology |
|--------|-----------|
| Framework | Flask (Python) |
| Frontend | HTML5, Jinja2 templates, Tailwind CSS (static prebuilt file) |
| Databases | SQLite (users/patient demographics/ relational), MongoDB Atlas (assessments & emergency contacts) |
| CSRF & Forms | Manual CSRF token (hidden input stored in session) |
| Auth | Session-based authentication, Werkzeug password hashing |
| Dev / Tools | python-dotenv, Faker, unittest |
| CSS build (optional) | Tailwind CLI / npm (only if you intend to rebuild CSS) |

## Installation & Setup

1. Clone the repository
```bash
git clone https://github.com/CS-LTU/com7033-assignment-AugustineMayaki.git
cd com7033-assignment-AugustineMayaki
```

2. Create & activate virtual environment, install Python deps
macOS / Linux:
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
Windows (PowerShell):
```powershell
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

3. Tailwind / Node notes (optional)
- static/css/tailwind.css is provided. Node/npm is NOT required to run the app.
- If you need to modify Tailwind sources, install Node and run the build steps described in the repo (tailwind.config.js present).

## Environment variables (copy/paste)

Copy/paste this block to create a .env file in the project root (adjust values before use):

```bash

FLASK_SECRET_KEY=your-secure-secret-key
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/
MONGODB_NAME=neuropredict_db
MONGODB_PATIENT_ASSESSMENTS_COLLECTION=patient_assessments
MONGODB_EMERGENCY_CONTACT_COLL=patient_emergency_contacts
```

Notes:
- FLASK_SECRET_KEY must be set for secure sessions and CSRF token generation.
- If MongoDB variables are not configured, MongoDB-backed features will fail.

## Database seeding

- On the first run the application will automatically seed SQLite (and MongoDB documents where configured). You do not need to run a separate seed step on a fresh install.
- If you need to re-seed for development, remove the seed flag (e.g., delete `instance/.db_seeded` if present) and run:
```bash
python seed_db.py
```

## Run the application

With virtualenv active:
```bash
python app.py
```
Default host/port http://localhost:5000/. 

## Sample employees (first three rows from csv/employees.csv)

| Employee ID | Name           | Email                            | Role       |
|------------:|----------------|----------------------------------|------------|
| EMP001      | John Smith     | john.smith@neuropredict.com      | doctor     |
| EMP002      | Sarah Johnson  | sarah.johnson@neuropredict.com   | nurse      |
| EMP003      | Michael Brown  | michael.brown@neuropredict.com   | super admin|

(These entries are present in `employees.csv` and may be used to create account)

## API & Routes Reference (server-rendered HTML forms — POST for modify)

### Authentication & Sessions
| Method | Route | Access | Description | Required fields |
|-------:|:-----:|:------:|------------:|-----------------|
| GET | / | Public | Login page | — |
| POST | / | Public | Login submit | email, password |
| GET | /register | Public | Employee/user registration page | — |
| POST | /register | Public | Create account | employee_id, email, password |
| GET | /logout | Authenticated | Logout (clear session) | — |

### User management (Admin)
| Method | Route | Access | Description | Required fields |
|-------:|:-----:|:------:|------------:|-----------------|
| GET | /users-management | Admin | View users list | — |
| POST | /deactivate-user/<user_id> | Admin | Deactivate user | — |
| POST | /activate-user/<user_id> | Admin | Activate user | — |

### Patients & Assessments
| Method | Route | Access | Description | Required fields |
|-------:|:-----:|:------:|------------:|-----------------|
| GET | /patient-management | Authenticated | Patients dashboard/list | — |
| POST | /register-patient | Authenticated | Create patient | first_name, last_name, date_of_birth, email, gender |
| GET | /patient-management/patient/<patient_id> | Authenticated | View patient details | — |
| POST | /patient-management/patient/<patient_id>/update | Authenticated | Update patient | first_name, last_name, date_of_birth, gender |
| POST | /patient-management/patient/<patient_id>/delete | Admin | Delete patient | — |
| POST | /patient-management/patient/<patient_id>/assessments | Authenticated | Add assessment (MongoDB) | work_type, ever_married, residence_type, avg_glucose_level, hypertensive_status, bmi, smoking_status |

### Emergency contacts (MongoDB-backed)
| Method | Route | Access | Description | Required fields |
|-------:|:-----:|:------:|------------:|-----------------|
| POST | /patient-management/patient/<patient_id>/emergency-contact/add | Authenticated | Add contact (max 2 per patient) | first_name, last_name, phone_number, relationship |
| POST | /patient-management/patient/<patient_id>/emergency-contact/<contact_id>/update | Authenticated | Update contact | first_name, last_name, phone_number, relationship |
| POST | /patient-management/patient/<patient_id>/emergency-contact/<contact_id>/delete | Authenticated | Delete contact | — |

## Input Validation Rules

| Field | Validation |
|------|-----------|
| Email | Regex: `^[\w\.-]+@[\w\.-]+\.\w+$` |
| Password | Minimum 8 chars, recommend complexity (upper, lower, digit, special) |
| Date of birth | YYYY-MM-DD, reasonable range (e.g., 1900–today) |
| BMI | Float, sensible medical range (e.g., 10–100) |
| Average glucose | Float, sensible range (e.g., 0–500) |

Server-side validation is enforced on all modifying endpoints; templates re-populate submitted values and show validation errors when needed.

## Forms & CSRF (manual token implementation)

This project uses a manual CSRF token approach (hidden input) — Flask-WTF is NOT used.

Typical pattern:



- In template:
```html
<form method="post" action="{{ url_for('some_post_route') }}">
  <input type="hidden" name="csrf_token" value="{{ csrf_token }}">
  <!-- other inputs -->
  <button type="submit">Submit</button>
</form>
```

## Pagination & UI Notes

- Lists use server-side pagination (10 records per page by default).
- Dashboard is server-rendered and hides/shows UI elements based on the logged-in user's role (server-side). Endpoints remain protected by RBAC decorators.

## Testing

Run unit tests:
```bash
python test.py
```
Ensure dependencies from `requirements.txt` are installed and any required environment variables are set prior to running tests.

## Security Notes & Controls

- CSRF protection via manual hidden-token approach
- Passwords hashed using Werkzeug (no plaintext storage)
- Parameterized SQL queries to reduce SQL injection risk
- Server-side validation and sanitisation of form inputs
- Jinja2 auto-escaping to mitigate XSS
- RBAC enforced with decorators (`@auth_required`, `@admin_required`, etc.)
- FLASK_SECRET_KEY used for session cryptography and token generation

## Design Rationale

- Server-rendered HTML + POST-only flows simplify validation and browser compatibility, and reduce client-side attack surface.
- SQLite chosen for authentication/relational data for portability and simple seeding.
- MongoDB chosen for assessments for schema flexibility as clinical assessment fields evolve.
- Manual CSRF tokens give explicit, auditable protection behaviour without adding another extension dependency.

## Acknowledgements

Developed by Augustine Mayaki as part of COM7033 (Secure Software Development).  
Acknowledgements: WHO stroke dataset, Flask community, Tailwind CSS, COM7033 course at Leeds Trinity University.