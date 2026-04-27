# Isocentre

Unofficial McMaster Medical & Biological Physics guide built with Flask, Jinja, SQLAlchemy, PostgreSQL, and lightweight browser-side tools.

## Local setup

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
export DATABASE_URL="postgresql://..."
export SECRET_KEY="change-me"
export ADMIN_PASSWORD="change-me"
export SITE_BASE_URL="http://127.0.0.1:5000"
flask --app wsgi:app db upgrade
flask --app wsgi:app seed
gunicorn "wsgi:app" --bind 127.0.0.1:5000
```

## Railway

Set these environment variables in Railway:

- `DATABASE_URL`
- `SECRET_KEY`
- `ADMIN_PASSWORD`
- `SITE_BASE_URL`
- `GOOGLE_ANALYTICS_ID` (defaults to `G-KZ430V2G5C`)

`DATABASE_URL` must point at the Railway Postgres service. If it is missing, the app refuses to boot on Railway instead of falling back to SQLite.

Community submissions and mentor messages use Isocentre's built-in notification inbox. SMTP is not required for the MVP.

Railway can start the app with the included `Procfile`:

```bash
flask --app wsgi:app db upgrade && flask --app wsgi:app seed && gunicorn "wsgi:app"
```

The start command runs migrations and the idempotent seed before booting Gunicorn, which prevents fresh Railway databases from failing with missing-table errors such as `relation "page" does not exist`. If you run commands manually, use:

```bash
flask --app wsgi:app db upgrade
flask --app wsgi:app seed
```

The app does not commit secrets. Seeded official links and student-facing content are stored in PostgreSQL.

## Content and moderation

Run `flask --app wsgi:app seed` after migrations to load the source-aligned 2025-2026 program content, course guides, requirement rules, and official resources. Community submissions stay private until an admin approves them. Submitters receive in-app notifications when moderation changes.

The admin panel is available at `/admin` and is protected by `ADMIN_PASSWORD`. Public pages use lightweight per-process caching; admin moderation and seed refreshes clear the cache.

## Student accounts

Students can create a local Isocentre account to save course plans, bookmark guides, submit reviews, join the mentor directory, message mentors, and see a personal dashboard. Account passwords are stored with Werkzeug password hashing. Public reviews, mentor profiles, and questions enter moderation from the signed-in account and updates appear in `/notifications`.

Useful routes:

- `/guide-map` for the structured site flow
- `/search` for global guide/course/resource search
- `/dashboard` for saved guides, planner state, and requirement pulse
- `/planner` for completed/planned/interested courses
- `/notifications` for moderation updates, course-review activity, and mentor-message alerts
- `/messages` for the mentor messaging inbox
