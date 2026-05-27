# FastAPI Production-Ready Blueprint

![Python](https://img.shields.io/badge/Python-3.13+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg?logo=fastapi)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-316192.svg?logo=postgresql)
![Docker](https://img.shields.io/badge/Docker-Enabled-2496ED.svg?logo=docker)
![License](https://img.shields.io/badge/License-MIT-green.svg)

A robust, async-first FastAPI Blueprint designed to accelerate the development of secure and scalable web applications.

## 💡 Why This Blueprint?

In today's fast-paced market, shipping quickly is a key selling point. I repeatedly found myself losing days deciding on project structures or setting up baseline authentication for FastAPI, sometimes even falling back to heavier frameworks just for their "batteries-included" convenience.

While third-party FastAPI auth libraries or massive boilerplates exist, they often hide the implementation details or come stuffed with bloat that takes days to strip away. I built this setup to solve that problem. It provides exactly what you need to start a new project, a highly secure, production-ready authentication and database foundation while keeping the ultimate superpower of control entirely in your hands. Zero bloat, out-of-the-box security, and fast shipping.

## ✨ Key Features & Technical Details

* **Modern Async Stack:** Fully asynchronous operations using FastAPI, SQLAlchemy 2.0 (Asyncpg), and Async Alembic migrations.
* **Hardened Authentication:** Features JWT-based auth with HttpOnly/Secure cookies, JTI-based refresh token rotation (with session wipe on theft), Argon2 password hashing via `pwdlib`, and strict Pydantic password validators.
* **Enterprise SSO:** Built-in OAuth2 integration for Google and GitHub single sign-on via `Authlib` and `itsdangerous` SessionMiddleware.
* **User Management:** Registration, login, profile updates, and role-based access control (User, Admin, Superuser).
* **Email Services:** Integrated OTP-based email verification and password reset flows using `fastapi-mail`.
* **Security & Reliability:** Utilizes IP-based rate limiting via `slowapi` to prevent brute-force attacks, alongside background tasks for automated database maintenance.
* **Structured Logging:** Configured with `structlog` to output JSON logs, making it instantly compatible with observability stacks like ELK or Grafana Loki.
* **Containerization:** Fully dockerized with specialized configurations for both local development and zero-downtime production deployments.
* **Dependency Management:** Uses `uv` for incredibly fast package management and dependency resolution.

## 🏗️ Tech Stack

* **Framework:** FastAPI
* **Database & ORM:** PostgreSQL, SQLAlchemy 2.0, Asyncpg, Alembic
* **Authentication:** PyJWT, Pwdlib (Argon2), Authlib
* **Infrastructure:** Docker, Docker Compose, GitHub Actions
* **Tooling:** uv, Uvicorn, Gunicorn, Structlog

## 📂 Project Structure

```text
├── app/
│   ├── api/          # API routers, endpoints (auth, sso, users), and dependencies
│   ├── core/         # App configuration, security, db setup, rate limiting, and logging
│   ├── models/       # SQLAlchemy async database models
│   ├── schemas/      # Pydantic models for strict request/response validation
│   └── services/     # Business logic layer
├── alembic/          # Database migration scripts (Async configured)
├── .github/          # CI/CD deployment automation templates
├── pyproject.toml    # Project metadata and uv dependencies
└── docker-compose.*  # Docker orchestration files
```

---

## 🛠️ Local Development

For the best developer experience, this project uses a **Hybrid** approach. The database and pgAdmin run inside Docker, while the FastAPI application runs directly on your machine to enable instant hot-reloading.

### Prerequisites

* [Docker](https://www.docker.com/) and Docker Compose
* Python 3.13+ (Don't worry, `uv` will install this automatically if you don't have it!)
* [uv](https://github.com/astral-sh/uv) (for incredibly fast dependency management)

### 1. Environment Setup

Clone the repository and set up your environment variables. The `.env` file is the master control for your local project name and secrets.

```bash
git clone https://github.com/prog-zone/fastapi_setup
cd fastapi_setup
cp .env.example .env
```

> **🔒 Pro-Tip: Commit your `uv.lock` file!**
> Because this is a deployable application (not a PyPI library), you want **reproducible builds**. Make sure `uv.lock` is **removed** from your `.gitignore` and committed to your repository. This guarantees that your local machine and your production server are all running the exact same dependency versions, preventing the dreaded "it worked on my machine" bug 😎.

### 2. Start the Infrastructure

Spin up the local Postgres database and pgAdmin interface via Docker:

```bash
docker compose -f docker-compose.local.yml up -d
```

*(pgAdmin is now available at `http://localhost:5050`)*

### 3. Run the Application

Install the dependencies, apply database migrations, and start the FastAPI server with hot-reloading enabled:

```bash
uv sync
uv run alembic upgrade head
uv run fastapi dev
```

* **API Health Check:** `http://localhost:8000/api/v1/health`
* **Interactive API Docs:** `http://localhost:8000/docs`

---

## 🚢 Production Deployment

This template includes a robust, seamless deployment architecture designed to keep your production server stateless and clean.

### The Master Script (`deploy.sh`)

For quick deployments to a VPS, use the included `deploy.sh` script. It automatically detects versions, backs up your database, and rebuilds your Docker containers without modifying any files on your production server.

1. **The Source of Truth:** Update your project `version` in `pyproject.toml` locally, then push to your repository.
2. Pull the code on your production server:

```bash
git pull origin main
```

3. Run the deployment script:

```bash
chmod +x deploy.sh
./deploy.sh
```

### 🚀 Automated CI/CD (GitHub Actions)

Ready to fully automate? This boilerplate includes a pre-configured "Smart Server" GitHub Action template.

Navigate to `.github/workflows/deploy.yml.example`. Simply remove the `.example` extension, add your VPS SSH credentials to your GitHub Repository Secrets, and your code will automatically test and deploy to your server the moment you merge to `main`.

---

## 🧪 Testing

This template is configured for testing using `pytest` and `httpx`. To run the test suite locally:

```bash
uv run pytest
```

## 🛡️ License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/prog-zone/fastapi_setup?tab=MIT-1-ov-file) file for details.