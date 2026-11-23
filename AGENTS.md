# AGENTS.md

Repository knowledge for AI agents working on AroundU.

## What this is

A Flask 3 app where students apply to events hosted by other colleges and
organizers approve applications. App-factory pattern with three blueprints.

## Commands

```bash
# setup
python -m venv .venv && . .venv/bin/activate
pip install -r requirements-dev.txt

# run
flask --app app run --debug

# database
flask --app app seed --drop     # wipe and reseed demo data
flask --app app init-db         # create missing tables

# tests
python -m pytest
```

## Layout

- `app.py` — `create_app()`, error handlers, CLI commands. `app` is created at
  import time so `gunicorn app:app` works.
- `config.py` — env-driven config; `TestingConfig` is used by pytest.
- `extensions.py` — `db`, `login_manager`, `csrf` singletons. Import these, never
  construct new ones.
- `models.py` — `User`, `Event`, `Registration`. Table names are plural.
- `routes/` — `auth`, `main`, `events` blueprints.
- `templates/` — Jinja. Shared card markup lives in `templates/macros.html`.
- `static/` — plain CSS and JS, no build step.

## Conventions

- Every POST form needs `<input type="hidden" name="csrf_token" value="{{ csrf_token() }}">`.
- Enforce permissions on the server with `abort(403)`, not only in templates.
- Validate and normalise form input in the route before touching the database.
- `Event.date` is a `db.Date`; `created_at` / `applied_at` are naive UTC.
- Capacity counts all registrations (pending + accepted).
- Keep `aroundu.db` committed and seeded — it is the demo database.
- Do not add front-end frameworks or a build step.

## Gotchas

- `User.events_organized` and `User.registrations` use `lazy="selectin"`.
- `Event.registrations` is loaded eagerly so `|length` works in templates.
- The login route accepts a safe relative `next` parameter.
- Templates reference `current_user.is_organizer` / `current_user.is_student`.

## Frontend

The UI is a single hand-written design system in `static/css/style.css`
(no framework, no build step). Keep it that way.

- **Tokens** live in `:root` (`--bg`, `--surface`, `--accent`, `--font-*`,
  `--header-h`). Reuse them; do not hard-code new colours.
- **Typography**: Space Grotesk for display, Inter for body, JetBrains Mono for
  technical labels. Mono labels are uppercase with wide letter-spacing.
- **Layout primitives**: `.container`, `.section`, `.panel`, `.stat-grid`,
  `.event-grid`, `.form-shell`, `.event-layout`.
- **Components**: buttons (`.btn-primary` / `.btn-outline` / `.btn-ghost`),
  `.tag`, `.pill`, `.status-pill--{pending,accepted,rejected}`, `.event-card`,
  `.spotlight`, `.data-table`, `.filter-tabs`.
- **Icons** come from the `icon(name, size)` macro in `templates/macros.html`.
  Add new inline SVGs there, never a font or CDN icon pack.
- **Cards** are rendered by the `event_card(event)` macro so home, dashboard and
  related-events stay identical.
- **JS** in `static/js/main.js` is progressive enhancement only: nav, reveal,
  counters, toasts, confirm prompts, copy, ICS, CSV, filters. Every page must
  still work with JS disabled.
- Bump the `v='N'` query on the CSS/JS URLs in `base.html` after changing them
  so browsers do not serve stale assets.
