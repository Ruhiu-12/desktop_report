# TechDesk Reporter - Workflow Documentation

## Overview

TechDesk Reporter is a desktop support ticketing system for university computer labs. Users report issues, technicians investigate and fix them, and analysts verify the work quality.

---

## User Roles

| Role | Access Level |
|------|-------------|
| **User** | Create cases, view own cases, add notes |
| **Technician** | View assigned cases, submit reports, add notes |
| **Analyst** | Review reports, approve/reject work |
| **Admin** | Manage all cases, assign technicians, manage users |
| **Super Admin** | Full access including delete |

---

## Complete Workflow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        TECHDESK REPORTER - WORKFLOW                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌──────────┐                                                               │
│  │   USER   │  Creates a case (title, description, priority, optional image)│
│  └────┬─────┘                                                               │
│       │                                                                     │
│       ▼ Status: NEW                                                         │
│  ┌──────────┐                                                               │
│  │  ADMIN   │  Reviews case, assigns a technician                           │
│  └────┬─────┘                                                               │
│       │                                                                     │
│       ▼ Status: ASSIGNED                                                    │
│  ┌────────────┐                                                             │
│  │ TECHNICIAN │  Investigates, updates status to "In Progress"              │
│  └────┬───────┘  Can add notes (e.g., "parts being imported")               │
│       │                                                                     │
│       ▼ Status: IN_PROGRESS                                                 │
│  ┌────────────┐                                                             │
│  │ TECHNICIAN │  Completes work, submits report with:                       │
│  └────┬───────┘  - Findings                                                 │
│       │          - Solution provided                                        │
│       │          - Evidence photo (optional)                                │
│       │          - Can add notes about delays/issues                        │
│       ▼ Status: PENDING_REVIEW                                              │
│  ┌──────────┐                                                               │
│  │ ANALYST  │  Reviews technician's report                                  │
│  └────┬─────┘  Approves → Case CLOSED                                       │
│       │         Rejects → Status back to IN_PROGRESS (tech must redo)       │
│       ▼                                                                     │
│  ┌──────────┐                                                               │
│  │   USER   │  Sees case is CLOSED, can now use desktop                    │
│  └──────────┘                                                               │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Status Flow

```
NEW ──► ASSIGNED ──► IN_PROGRESS ──► PENDING_REVIEW ──► CLOSED
  ▲                      ▲                │
  │                      │                └── Reject ──► IN_PROGRESS
  │                      │                    (back to technician)
  │                      │
  │                      └── Technician can toggle between these
  │                          while working
  │
  └── User creates case here
```

### Status Definitions

| Status | Meaning | Who Sets It |
|--------|---------|-------------|
| **NEW** | Case just created, waiting for assignment | System (auto) |
| **ASSIGNED** | Technician assigned to investigate | Admin |
| **IN_PROGRESS** | Technician actively working on issue | Technician/Admin |
| **PENDING_REVIEW** | Report submitted, waiting for analyst approval | Technician |
| **CLOSED** | Issue resolved, case complete | Analyst/Admin |

---

## Role Responsibilities

### User
- **Creates cases** with title, description, priority, optional screenshot
- **Views own cases** only (cannot see other users' cases)
- **Adds notes** to own cases (e.g., "additional info about the problem")
- **Sees status updates** and audit trail
- **Cannot** close cases or change status

### Technician
- **Views assigned cases** only (not all cases)
- **Updates status** between "In Progress" and "Pending Review"
- **Submits report** with:
  - Findings (what was wrong)
  - Solution provided (what was done)
  - Evidence photo (proof of work)
- **Adds notes** (e.g., "parts being imported, will take 2 weeks")
- **Cannot** close cases (analyst must approve)

### Analyst
- **Views all reports** pending review
- **Reviews report** including findings, solution, and evidence photo
- **Approves report** → Case closes, user notified
- **Rejects report** → Status returns to "In Progress", technician must redo
- **Adds notes** to cases
- **Cannot** create cases or assign technicians

### Admin
- **Views ALL cases** in the system
- **Assigns technicians** to new cases
- **Updates status** (In Progress / Pending Review / Closed)
- **Manages users** (promotes/demotes roles)
- **Views all reports**
- **Adds notes** to any case

### Super Admin
- **Everything admin can do**
- **Delete** cases and users (if needed)

---

## Anti-Deception Measures

| Feature | Purpose |
|---------|---------|
| **Audit Log** | Tracks every status change with user ID and timestamp |
| **Notes** | Users can leave visible comments about delays or issues |
| **Evidence Photos** | Technicians upload proof of work done |
| **Role Restrictions** | Technicians cannot close their own cases |
| **Analyst Approval** | Independent review before case closes |
| **Timestamps** | All actions recorded with exact time |

---

## Page Structure

### Authentication Pages
- `/accounts/login` - Login with identifier (adm/employee number)
- `/accounts/register` - Create new account (defaults to User role)
- `/accounts/forgot-password` - Reset password via email

### User Pages
- `/dashboard` - Personal dashboard with own cases
- `/cases/` - List of own cases
- `/cases/create/` - Report a new issue
- `/cases/<id>/` - Case details, notes, audit log

### Technician Pages
- `/dashboard` - Assigned cases summary
- `/cases/` - List of assigned cases
- `/cases/<id>/` - Case details, update status, submit report
- `/reports/create/<case_id>/` - Submit report with findings and evidence

### Analyst Pages
- `/dashboard` - Pending reviews summary
- `/reports/` - List of all reports
- `/reports/<id>/` - View report, approve/reject

### Admin Pages
- `/dashboard` - System overview (total cases, users)
- `/cases/` - All cases in system
- `/cases/<id>/assign/` - Assign technician to case
- `/users/` - Manage user accounts and roles
- `/reports/` - View all reports

---

## Technical Stack

- **Backend:** Django 6.0 (Python)
- **Frontend:** Tailwind CSS (CDN)
- **Database:** SQLite
- **Email:** Console backend (development) / SMTP (production)
- **Authentication:** Custom user model with email verification

---

## Data Models

### Case
- Title, Description, Priority (Low/Medium/High/Critical)
- Status (New/Assigned/In Progress/Pending Review/Closed)
- Created By (User), Assigned Technician
- Optional screenshot/image
- Created/Updated timestamps

### Report
- Linked to Case (one-to-one)
- Technician who submitted
- Findings, Solution Provided
- Optional evidence photo
- Approval status (Pending/Approved)
- Submission timestamp

### CaseNote
- Linked to Case
- Author, Content, Timestamp

### CaseAuditLog
- Linked to Case
- Action description, Changed By, Timestamp

---

*Document generated for TechDesk Reporter project*
