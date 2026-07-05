# TechDesk Reporter

A web-based desktop support ticketing system for university computer labs. Users report issues, technicians investigate and fix them, and analysts verify the work quality.

## Features

- **Role-based access control** - User, Technician, Analyst, Admin, Super Admin
- **Case management** - Create, assign, track, and resolve desktop issues
- **Report submission** - Technicians submit findings with evidence photos
- **Analyst approval** - Independent review before cases close
- **Notes system** - Add comments and updates to cases
- **Audit trail** - Complete history of all actions with timestamps
- **Email verification** - Secure account registration

## Tech Stack

- **Backend:** Django 6.0 (Python)
- **Frontend:** Tailwind CSS (CDN)
- **Database:** SQLite
- **Email:** Console backend (development)

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/Ruhiu-12/desktop_report.git
cd desktop_report
```

### 2. Create and activate virtual environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Create .env file

Create a `.env` file in the project root with:

```
SECRET_KEY=your-secret-key-here
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

### 5. Run migrations

```bash
python manage.py migrate
```

### 6. Create superuser

```bash
python manage.py createsuperuser
```

### 7. Start development server

```bash
python manage.py runserver
```

Visit http://127.0.0.1:8000

## User Roles

| Role | Capabilities |
|------|-------------|
| **User** | Create cases, view own cases, add notes |
| **Technician** | View assigned cases, submit reports with evidence |
| **Analyst** | Review reports, approve/reject work |
| **Admin** | Manage all cases, assign technicians, manage users |
| **Super Admin** | Full access including delete |

## Workflow

1. **User** creates a case (title, description, priority, optional screenshot)
2. **Admin** assigns a technician to the case
3. **Technician** investigates, updates status, submits report with findings and evidence
4. **Analyst** reviews the report and approves or rejects
5. **User** sees the case is closed

See [WORKFLOW.md](WORKFLOW.md) for detailed workflow documentation.

## Project Structure

```
desktop_report/
├── accounts/           # User authentication and management
├── cases/              # Case management and notes
├── reports/            # Report submission and review
├── dashboard/          # Role-based dashboards
├── users/              # Admin user management
├── templates/          # HTML templates
│   ├── accounts/       # Auth pages (login, register, etc.)
│   ├── cases/          # Case pages
│   ├── reports/        # Report pages
│   ├── users/          # User management pages
│   ├── dashboard/      # Dashboard pages
│   └── components/     # Reusable components (sidebar, topbar)
├── static/             # CSS and JavaScript
├── config/             # Django settings and URLs
├── WORKFLOW.md         # Detailed workflow documentation
└── manage.py
```

## License

This project is for educational purposes.
