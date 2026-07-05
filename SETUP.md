# TechDesk Reporter - Partner Setup Guide

## Quick Start

```bash
git clone https://github.com/Ruhiu-12/desktop_report.git
cd desktop_report
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
echo SECRET_KEY=my-secret-key-123 > .env
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Visit http://127.0.0.1:8000

---

## Create Test Users

After setting up, run this command to create test users for all roles:

```bash
python manage.py shell -c "
from accounts.models import CustomUser
from django.contrib.auth.models import Group

# Create groups
for role in ['admin', 'technician', 'analyst']:
    Group.objects.get_or_create(name=role)

# Create superuser (if not already created)
if not CustomUser.objects.filter(identifier='admin').exists():
    CustomUser.objects.create_superuser('admin', 'admin@test.com', 'admin123')
    print('Created: admin / admin123')

# Create test users
users = [
    ('tech1', 'tech@test.com', 'pass1234', 'technician'),
    ('analyst1', 'analyst@test.com', 'pass1234', 'analyst'),
    ('user1', 'user@test.com', 'pass1234', None),
]

for ident, email, pwd, role in users:
    if not CustomUser.objects.filter(identifier=ident).exists():
        u = CustomUser.objects.create_user(ident, email, pwd)
        u.is_verified = True
        u.save()
        if role:
            u.groups.add(Group.objects.get(name=role))
        print(f'Created: {ident} / {pwd} ({role or \"user\"})')

print('Done!')
"
```

---

## Test Accounts

| Role | Identifier | Password |
|------|------------|----------|
| Super Admin | admin | admin123 |
| Technician | tech1 | pass1234 |
| Analyst | analyst1 | pass1234 |
| User | user1 | pass1234 |

---

## Test Workflow

1. Login as **user1** → Create a case
2. Login as **admin** → Assign case to tech1
3. Login as **tech1** → Update status to "In Progress" → Submit report
4. Login as **analyst1** → Approve the report
5. Login as **user1** → Verify case is closed

---

## Project Files

```
desktop_report/
├── WORKFLOW.md         # Complete workflow documentation
├── SETUP.md            # This file
├── README.md           # Project overview
├── accounts/           # User auth
├── cases/              # Cases and notes
├── reports/            # Reports
├── dashboard/          # Dashboards
├── users/              # User management
├── templates/          # HTML templates
├── static/             # CSS/JS
└── config/             # Settings
```

---

## Common Issues

**"ModuleNotFoundError: No module named 'decouple'"**
```bash
pip install python-decouple
```

**"SECRET_KEY not set"**
```bash
echo SECRET_KEY=any-random-string > .env
```

**Email error on register**
Already fixed - emails print to terminal instead of sending.

**Can't see Submit Report button**
Make sure you're logged in as the technician assigned to the case.

---

*Generated for partner setup*
