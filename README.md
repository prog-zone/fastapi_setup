# FastAPI Production-Ready Starter Template

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg?logo=fastapi)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-316192.svg?logo=postgresql)
![Docker](https://img.shields.io/badge/Docker-Enabled-2496ED.svg?logo=docker)
![License](https://img.shields.io/badge/License-MIT-green.svg)

A robust, async-first FastAPI starter template designed to accelerate the development of secure and scalable web applications. It comes pre-configured with industry best practices, including async database operations, secure authentication, background tasks, and containerization.

## ✨ Key Features

* **Modern Async Architecture:** Built with FastAPI, SQLAlchemy 2.0 (Async), and PostgreSQL.
* **Hardened Security:** JWT-based authentication stored securely in `HttpOnly` cookies, password hashing via Argon2, and route-level rate limiting using `slowapi`.
* **User Management System:** Out-of-the-box user registration, role-based access control (User/Admin/Superuser), and profile management.
* **Email Workflows:** Integrated OTP-based email verification and password reset flows via `fastapi-mail` and background tasks.
* **Developer Experience:** Lightning-fast dependency management using `uv` and structured JSON logging with `structlog`.
* **Container Ready:** Fully dockerized with separate configurations for local development (including pgAdmin) and API deployment.

## 🏗️ Tech Stack

* **Framework:** FastAPI
* **Database & ORM:** PostgreSQL, SQLAlchemy 2.0, Asyncpg, Alembic
* **Authentication:** PyJWT, Pwdlib (Argon2)
* **Infrastructure:** Docker, Docker Compose
* **Tooling:** uv, Uvicorn, Gunicorn, Structlog

## 📂 Project Structure

```text
├── app/
│   ├── api/          # API routers, dependency injection, and permissions
│   ├── core/         # App configuration, database setup, security, and logging
│   ├── models/       # SQLAlchemy database models
│   ├── schemas/      # Pydantic models for data validation
│   └── services/     # Core business logic layer
├── alembic/          # Database migration configurations and versions
├── pyproject.toml    # Project metadata and dependencies (uv)
└── docker-compose.* # Docker orchestration files
```

## 🚀 Getting Started

### Prerequisites

* [Docker](https://www.docker.com/) and Docker Compose
* Python 3.10+ (for local development)
* [uv](https://github.com/astral-sh/uv) (for local dependency management)

### 1. Environment Setup

Clone the repository and set up your environment variables:

```bash
git clone https://github.com/prog-zone/fastapi_setup
cd fastapi-setup
cp .env.example .env
```
*Make sure to update the `.env` file with your specific database credentials, JWT secrets, and SMTP settings.*

### 2. Running with Docker (API & Database)

This command starts the PostgreSQL database, automatically applies Alembic migrations, and spins up the FastAPI server via Gunicorn.

```bash
docker-compose up --build
```
* **API Health Check:** `http://localhost:8000/api/v1/health`
* **Interactive API Docs:** `http://localhost:8000/docs`

### 3. Local Development (Local API + Docker Database)

If you prefer to run the API locally on your host machine for easier debugging, while keeping the database and management tools containerized:

**Start the local database and pgAdmin:**
```bash
docker-compose -f docker-compose.local.yml up -d
```
* **pgAdmin:** `http://localhost:5050` (Login with credentials from `.env`)

**Install dependencies and run migrations:**
```bash
uv sync
alembic upgrade head
```

**Start the FastAPI development server:**
```bash
fastapi dev app/main.py
```

## 🛡️ License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.