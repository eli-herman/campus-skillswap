# Campus SkillSwap

[![CI](https://github.com/eli-herman/campus-skillswap/actions/workflows/ci.yml/badge.svg)](https://github.com/eli-herman/campus-skillswap/actions/workflows/ci.yml)

Campus SkillSwap is a beginner-friendly Django marketplace where students post and discover skills or services.

**Live site:** https://eherman234.pythonanywhere.com (demo login: `maya` / `demo1234`)

## Features

- Account registration, login, and logout
- Public skill browsing and detail pages
- Search by title or category
- Create, edit, and delete only your own posts
- Personal dashboard
- Star ratings and written reviews
- Django admin for managing posts and reviews

## 1. Set up the project

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Open `http://127.0.0.1:8000/`.

## 2. Project structure

- `campus_skillswap/settings.py` - Django settings
- `campus_skillswap/urls.py` - project-level login, logout, and app routes
- `skills/models.py` - Skill and Review database models
- `skills/forms.py` - account, listing, and review forms
- `skills/views.py` - function-based request handlers
- `skills/urls.py` - app routes
- `templates/skills/` - HTML templates
- `static/css/site.css` - green-and-gold styling

## 3. Ownership

Each `Skill` has an `owner` foreign key to Django's built-in `User`. Edit and delete views query `Skill.objects.filter(pk=pk, owner=request.user)`, preventing changes to another student's post.

## 4. Search

The `skill_list` function reads `q` and `category` from the URL. It uses `title__icontains` and `category__icontains` for beginner-friendly, case-insensitive title/category matches.

## 5. Reviews

Signed-in students who do not own a post can submit a 1-to-5 star rating and comment. The database allows one review per student per skill, and submitting again updates the existing review.

## 6. Check and test

```bash
ruff check .            # lint
ruff format .           # auto-format
python manage.py check
python manage.py test
```

GitHub Actions runs the same lint, format, migration and test checks on every push (`.github/workflows/ci.yml`).

## 7. Django admin

Visit `http://127.0.0.1:8000/admin/` and sign in with the superuser account created above.

## 8. Add demo content

```bash
python manage.py seed_campus_skills
```

This adds repeatable demo accounts, listings, reviews, a booking, messages, and a report. Demo passwords are `demo1234`. Reset demo users and their related records with:

```bash
python manage.py seed_campus_skills --reset
```

## 9. Deployment (PythonAnywhere)

The site runs on PythonAnywhere's free tier with SQLite.

- **Settings:** production reads `DJANGO_DEBUG=0` and `DJANGO_SECRET_KEY` from environment variables set in the PythonAnywhere WSGI file. With debug off, cookies are HTTPS-only and HTTP redirects to HTTPS.
- **Deploying an update:** push to `main`, then in a PythonAnywhere Bash console run:

  ```bash
  ~/campus-skillswap/scripts/deploy.sh
  ```

  It backs up the database, pulls the code, installs requirements, runs migrations, collects static files and reloads the site. `db.sqlite3` is git-ignored, so a deploy never overwrites live data.
- **Backups:** `scripts/backup_db.sh` runs as a daily scheduled task and keeps the newest 7 copies in `~/backups`.
- **Errors:** 500 tracebacks go to the web app's error log on the PythonAnywhere **Web** tab.
