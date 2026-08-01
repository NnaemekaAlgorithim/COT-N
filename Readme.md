# COT-N Django Project

This repository has been converted from a Go service into a Django project.

## Run locally

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

## Run with Docker Compose

```bash
docker compose up --build
```

The app will be available at http://localhost:8000 and through nginx at http://localhost/.
