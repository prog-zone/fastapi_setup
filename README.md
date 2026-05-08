# FastAPI Production-Ready Starter Template

![Python](https://img.shields.io/badge/Python-3.13+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg?logo=fastapi)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-316192.svg?logo=postgresql)
![Docker](https://img.shields.io/badge/Docker-Enabled-2496ED.svg?logo=docker)
![License](https://img.shields.io/badge/License-MIT-green.svg)

A robust, async-first FastAPI starter template designed to accelerate the development of secure and scalable web applications. 

## 💡 Why This Template?

In today's fast-paced market, shipping quickly is a key selling point. I repeatedly found myself losing days deciding on project structures or setting up baseline authentication for FastAPI, sometimes even retreating to Django just for its "batteries-included" convenience.

While third-party FastAPI auth libraries or massive boilerplates exist, they often hide the implementation details or come stuffed with bloat that takes days to strip away. I built this setup to solve that problem. It provides exactly what you need to start a new project—a highly secure, production-ready authentication and database foundation—while keeping the ultimate superpower of control entirely in your hands. Zero bloat, out-of-the-box security, and fast shipping.

## ✨ Key Features & Technical Details

* **Modern Async Stack:** Fully asynchronous operations using FastAPI, SQLAlchemy 2.0 (Asyncpg), and Async Alembic migrations.
* **Hardened Authentication:**
* JWT-based auth utilizing **HttpOnly, Secure cookies** to prevent XSS.
* **JTI-based refresh token rotation** with built-in token theft detection (automatically wipes compromised sessions).
* Argon2 password hashing via `pwdlib`.
* Custom Pydantic validators enforcing strict password strength.


* **User Management:** Registration, login, profile updates, and role-based access control (User, Admin, Superuser).
* **Email Services:** Integrated OTP-based email verification and password reset flows using `fastapi-mail`.
* **Security & Reliability:**
* IP-based rate limiting via `slowapi` to prevent brute-force attacks.
* Background tasks for automated database maintenance (e.g., cleaning expired tokens).


* **Structured Logging:** Configured with `structlog` to output JSON logs, making it instantly compatible with observability stacks like ELK or Grafana Loki.
* **Containerization:** Fully dockerized with `docker-compose` setups for both the API and a local PostgreSQL + pgAdmin environment.
* **Dependency Management:** Uses `uv` for incredibly fast package management and dependency resolution.

## 🏗️ Tech Stack

* **Framework:** FastAPI
* **Database & ORM:** PostgreSQL, SQLAlchemy 2.0, Asyncpg, Alembic
* **Authentication:** PyJWT, Pwdlib (Argon2)
* **Infrastructure:** Docker, Docker Compose
* **Tooling:** uv, Uvicorn, Gunicorn, Structlog

## 📂 Project Structure

```text
├── app/
│   ├── api/          # API routers, endpoints, and dependency injections
│   ├── core/         # App configuration, security, db setup, rate limiting, and logging
│   ├── models/       # SQLAlchemy async database models
│   ├── schemas/      # Pydantic models for strict request/response validation
│   └── services/     # Business logic layer
├── alembic/          # Database migration scripts (Async configured)
├── pyproject.toml    # Project metadata and uv dependencies
└── docker-compose.*  # Docker orchestration files
```

---

## 🛠️ Local Development

### Prerequisites

* [Docker](https://www.docker.com/) and Docker Compose
* Python 3.13 (Don't worry, `uv` will install this automatically if you don't have it!)
* [uv](https://github.com/astral-sh/uv) (for incredibly fast dependency management)

### 1. Environment Setup

Clone the repository and set up your environment variables. The `.env` file is the master control for your local project name and secrets.

```bash
git clone https://github.com/prog-zone/fastapi_setup
cd fastapi_setup
cp .env.example .env
```
> **🔒 Pro-Tip: Commit your `uv.lock` file!**
> Because this is a deployable application (not a PyPI library), you want **reproducible builds**. Make sure `uv.lock` is **removed** from your `.gitignore` and committed to your repository. This guarantees that your local machine, your CI/CD pipeline, and your production server are all running the exact same dependency versions, preventing the dreaded "it worked on my machine" bug.


### 2. Choose Your Dev Workflow

**Option A: Full Docker (Easiest)**
Start the PostgreSQL database, automatically apply Alembic migrations, and spin up the FastAPI server via Gunicorn entirely inside Docker.

```bash
docker-compose up --build
```

**Option B: Hybrid (Local API + Docker Database)**
If you prefer to run the API locally on your host machine for faster debugging, while keeping the database and pgAdmin containerized:

1. Start the local database and pgAdmin:

```bash
docker-compose -f docker-compose.local.yml up -d
```

*(pgAdmin available at `http://localhost:5050`)*

2. Install dependencies and run migrations:

```bash
uv sync
alembic upgrade head
```

3. Start the FastAPI development server:

```bash
fastapi dev app/main.py
```

* **API Health Check:** `http://localhost:8000/api/v1/health`
* **Interactive API Docs:** `http://localhost:8000/docs`

---

## 🚢 Production Deployment

This template includes a robust, seamless deployment architecture designed to keep your production server stateless and clean.

### The Master Script (`deploy.sh`)

For quick deployments to a VPS, use the included `deploy.sh` script. It automatically detects versions, backs up your database, and rebuilds your Docker containers without modifying any files on your production server.

**How it works:**

1. **The Source of Truth:** Update your project `name` and `version` in `pyproject.toml` locally, then push to your server.
2. Pull the code on your server:

```bash
git pull origin main
```

3. Run the deployment script:

```bash
chmod +x deploy.sh
./deploy.sh
```

*Note: The script safely creates an automated `pg_dump` of your Postgres database before applying any container restarts.*

### 🚀 Level Up: Full CI/CD Pipeline

*Coming Soon: Instructions for unlocking the "Beast Mode" GitHub Actions pipeline for automated image registry builds and zero-touch VPS deployments.*

---

## 🧪 Testing

This template is configured for testing using `pytest` and `httpx`. To run the test suite locally:

```bash
uv run pytest
```

## 🛡️ License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/prog-zone/fastapi_setup?tab=MIT-1-ov-file) file for details.