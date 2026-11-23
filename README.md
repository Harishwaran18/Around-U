# AroundU

**Every campus. One stage.**

AroundU is a cross-college event platform. Students discover and apply to fests,
hackathons, workshops and sports meets hosted by any college — a tier 3 student
can walk into an IIT fest, and an IIT student can compete at a government college
hackathon. Organizers publish events and approve applications from one dashboard.

---

## Features

**For students**

- Browse every event with keyword search and college/category filters
- Apply in one click; withdraw before the event
- Track application status (pending / accepted / rejected) on a personal dashboard
- See seats remaining for capped events

**For organizers**

- Publish, edit and delete events
- Set capacity, cover image, venue, date and time
- Review applications and accept or reject each student
- Live counts of applications, accepted seats and pending reviews

**Platform**

- Email + password auth with hashed passwords (Werkzeug PBKDF2)
- CSRF protection on every form
- Server-side validation for all inputs
- Role-based access control (students cannot create events, organizers cannot apply)
- Friendly 403 / 404 / 500 pages
- `/healthz` endpoint for uptime checks
- Responsive dark UI with no front-end build step

---

## Tech stack

| Layer     | Choice                                        |
| --------- | --------------------------------------------- |
| Backend   | Python 3.12, Flask 3, Blueprints, app factory |
| Data      | SQLAlchemy 2 + Flask-SQLAlchemy               |
| Auth      | Flask-Login, Werkzeug password hashing        |
| Forms     | Plain HTML + Flask-WTF CSRF protection        |
| Database  | SQLite by default, PostgreSQL in production   |
| Server    | Gunicorn                                      |
| Tests     | pytest (18 end-to-end tests)                  |

---

## Quick start

```bash
git clone https://github.com/Harishwaran18/Around-U.git
cd Around-U

python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

pip install -r requirements.txt
flask --app app run --debug
```

Open <http://127.0.0.1:5000>.

The repository ships with a seeded `aroundu.db`, so the site is populated on the
first run. To rebuild the database at any time:

```bash
flask --app app seed --drop
```

### Demo accounts

All demo accounts use the password `password123`.

| Role      | Email                 | College                                   |
| --------- | --------------------- | ----------------------------------------- |
| Student   | `student@demo.com`    | Government College of Engineering, Salem  |
| Organizer | `events@iitm.ac.in`   | IIT Madras                                |
| Organizer | `events@gcesalem.edu.in` | Government College of Engineering, Salem |

Create your own organizer from the CLI:

```bash
flask --app app create-organizer
```

---

## Project structure

```text
Around-U/
├── app.py                  # Application factory, error handlers, CLI commands
├── config.py               # Environment-driven configuration
├── constants.py            # Roles, categories, colleges, limits
├── extensions.py           # db / login_manager / csrf singletons
├── models.py               # User, Event, Registration
├── seed_data.py            # Demo dataset
├── routes/
│   ├── auth.py             # Register, login, logout
│   ├── main.py             # Landing page, dashboard, health check
│   └── events.py           # Event CRUD, applications, approvals
├── templates/              # Jinja templates (base, macros, auth, events, errors)
├── static/
│   ├── css/style.css
│   ├── js/main.js
│   └── images/             # Logo and event placeholder
├── tests/                  # pytest fixtures and end-to-end tests
├── aroundu.db              # Seeded SQLite database (committed for the demo)
├── requirements.txt
├── Procfile                # Heroku / Railway process definition
├── runtime.txt             # Python version for Heroku
├── render.yaml             # One-click Render blueprint (web + Postgres)
└── Dockerfile
```

---

## Routes

| Method    | Path                                        | Access     |
| --------- | ------------------------------------------- | ---------- |
| GET       | `/`                                         | Public     |
| GET       | `/healthz`                                  | Public     |
| GET/POST  | `/register`                                 | Public     |
| GET/POST  | `/login`                                    | Public     |
| GET       | `/logout`                                   | Signed in  |
| GET       | `/dashboard`                                | Signed in  |
| GET/POST  | `/events/create`                            | Organizer  |
| GET       | `/events/<id>`                              | Public     |
| POST      | `/events/<id>/apply`                        | Student    |
| POST      | `/events/<id>/cancel`                       | Student    |
| GET       | `/events/<id>/manage`                       | Owner      |
| POST      | `/events/<id>/registrations/<rid>/<action>` | Owner      |
| GET/POST  | `/events/<id>/edit`                         | Owner      |
| POST      | `/events/<id>/delete`                       | Owner      |

`<action>` is `accept`, `reject` or `pending`.

---

## Configuration

Copy `.env.example` to `.env` for local development. Flask loads it automatically.

| Variable               | Default                    | Purpose                                       |
| ---------------------- | -------------------------- | --------------------------------------------- |
| `SECRET_KEY`           | `dev-secret-key-change-me` | Session signing key. **Set this in production.** |
| `DATABASE_URL`         | bundled SQLite file        | PostgreSQL or SQLite connection string        |
| `SESSION_COOKIE_SECURE`| `0`                        | Set to `1` when served over HTTPS             |
| `AUTO_CREATE_TABLES`   | `1`                        | Create missing tables on boot                 |
| `SEED_ON_STARTUP`      | `0`                        | Seed demo data when the database is empty     |
| `FLASK_DEBUG`          | unset                      | `1` enables the debugger locally              |

---

## Database

- **Local / demo:** SQLite file at `aroundu.db`. Nothing to install.
- **Production:** any PostgreSQL instance. Set `DATABASE_URL` and the app uses it
  automatically (`postgres://` URLs are normalised to `postgresql://`).
- Tables are created automatically on boot when `AUTO_CREATE_TABLES=1`.
- Tables: `users`, `events`, `registrations`. A registration is unique per
  student per event, enforced by a database constraint.

---

## Tests

```bash
pip install -r requirements-dev.txt
python -m pytest
```

The suite covers registration and login validation, role restrictions, event
creation and validation, duplicate applications, capacity limits, organizer
approvals, cross-organizer access, search filters and the health check.

---

## Deployment

See [DEPLOY.md](DEPLOY.md) for step-by-step instructions for Render, Railway,
Heroku and Docker. The fastest path is the Render blueprint:

1. Push this repository to GitHub.
2. In Render choose **New → Blueprint** and select the repository.
3. `render.yaml` creates the web service and a free PostgreSQL database.
4. Render generates `SECRET_KEY` and seeds the database on first boot.

The production start command is:

```bash
gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --threads 4 --timeout 60
```

---

## Security notes

- Passwords are never stored in plain text.
- Every state-changing form includes a CSRF token.
- Access control is enforced on the server, not only in the UI.
- Session cookies are HTTP-only and `SameSite=Lax`.
- Set `SECRET_KEY` and `SESSION_COOKIE_SECURE=1` before going live.

---

Built for students who want to see what the rest of the country is building.
