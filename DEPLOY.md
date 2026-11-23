# Deploying AroundU

AroundU is a standard Flask + Gunicorn app. It runs on SQLite with zero setup and
on PostgreSQL in production. Pick one of the options below.

Before you deploy, generate a secret key:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Keep it as `SECRET_KEY` in your host's environment variables.

---

## Option 1 — Render (recommended, free tier)

### One-click blueprint

1. Push this repository to GitHub (the `main` branch).
2. Sign in at <https://render.com> and choose **New → Blueprint**.
3. Select the repository. Render reads `render.yaml` and creates:
   - a Python web service
   - a free PostgreSQL database
   - a generated `SECRET_KEY`
4. Click **Apply**. Wait for the first build to finish.

`SEED_ON_STARTUP=1` is set in the blueprint, so the demo data is inserted the
first time the service boots with an empty database.

### Manual setup

1. **New → PostgreSQL**. Choose the free plan, create it and copy the
   **Internal Database URL**.
2. **New → Web Service**, connect the repository, and use:
   - **Runtime:** Python 3
   - **Build command:** `pip install -r requirements.txt`
   - **Start command:** `gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --threads 4 --timeout 60`
   - **Health check path:** `/healthz`
3. Add environment variables:
   - `SECRET_KEY` — your generated key
   - `DATABASE_URL` — the internal PostgreSQL URL
   - `SESSION_COOKIE_SECURE` — `1`
   - `AUTO_CREATE_TABLES` — `1`
4. Deploy. Tables are created automatically on the first request.

> Render's free PostgreSQL expires after a while. Upgrade the database or use
> another provider if you need it permanently.

---

## Option 2 — Railway

1. Create a project at <https://railway.app> and add **Deploy from GitHub repo**.
2. Add a **PostgreSQL** plugin. Railway exposes `DATABASE_URL` to the service.
3. Set the start command to:
   ```bash
   gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --threads 4 --timeout 60
   ```
4. Add `SECRET_KEY` and `SESSION_COOKIE_SECURE=1`.
5. Deploy.

---

## Option 3 — Heroku

The repository includes a `Procfile` and `runtime.txt`.

```bash
heroku create aroundu-app
heroku addons:create heroku-postgresql:essential-0
heroku config:set SECRET_KEY="<your-generated-key>"
heroku config:set SESSION_COOKIE_SECURE=1
git push heroku main
heroku open
```

Heroku injects `DATABASE_URL`; the app converts the `postgres://` scheme to
`postgresql://` automatically. Tables are created on first boot.

---

## Option 4 — Docker

```bash
docker build -t aroundu .
docker run -p 8000:8000 \
  -e SECRET_KEY="<your-generated-key>" \
  -e SEED_ON_STARTUP=1 \
  aroundu
```

Open <http://127.0.0.1:8000>.

To use PostgreSQL instead of the bundled SQLite file:

```bash
docker run -p 8000:8000 \
  -e SECRET_KEY="<your-generated-key>" \
  -e DATABASE_URL="postgresql://user:password@host:5432/aroundu" \
  aroundu
```

---

## Option 5 — Any VPS (Ubuntu + Gunicorn + Nginx)

```bash
sudo apt update
sudo apt install -y python3-venv nginx

git clone https://github.com/Harishwaran18/Around-U.git /var/www/aroundu
cd /var/www/aroundu
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt

export SECRET_KEY="<your-generated-key>"
.venv/bin/gunicorn app:app --bind 127.0.0.1:8000 --workers 2 --threads 4
```

Put Nginx in front of `127.0.0.1:8000` and manage the process with systemd or
Supervisor. Set `SESSION_COOKIE_SECURE=1` once HTTPS is enabled.

---

## Production checklist

- [ ] `SECRET_KEY` is a long random value (not the default)
- [ ] `SESSION_COOKIE_SECURE=1` and the site is served over HTTPS
- [ ] `DATABASE_URL` points at PostgreSQL (not the committed SQLite file)
- [ ] `FLASK_DEBUG` is not set
- [ ] `/healthz` returns `{"status":"ok"}` after deploy
- [ ] Demo accounts are removed or passwords changed before real use

---

## Troubleshooting

**`relation "users" does not exist`**
The app did not create tables. Set `AUTO_CREATE_TABLES=1`, or run
`flask --app app init-db` once against the production database.

**`could not connect to server` / database errors**
Check `DATABASE_URL`. It must be a full SQLAlchemy URL. The app rewrites
`postgres://` to `postgresql://`, but the username, password and database name
must be correct.

**`ModuleNotFoundError: No module named 'psycopg2'`**
`psycopg2-binary` is in `requirements.txt`. Make sure the build step ran
`pip install -r requirements.txt`.

**Styles missing**
Static files are served by Flask from `/static`. If you put a reverse proxy in
front, make sure it forwards `/static` to the app (or configure Nginx to serve
that directory directly).

**Session is lost after deploy**
`SECRET_KEY` changed between restarts. Set it once as an environment variable and
keep it stable.
