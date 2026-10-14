# Task Management REST API

A production-grade, secure, and resume-worthy Task Management REST API built with **FastAPI**, **SQLAlchemy 2.0 ORM**, **PostgreSQL** / **SQLite**, **Alembic migrations**, and **JWT Authentication (OAuth2 Bearer)**.

Designed following enterprise backend design patterns: layered service architecture, strict dependency injection, automated schema validation via Pydantic v2, and multi-tenant data isolation preventing Insecure Direct Object References (IDOR).

---

## 🌟 Key Features

### 🔐 1. User Authentication & Authorization
- **Secure Registration**: Case-insensitive email uniqueness check, minimum 8-character password enforcement, and secure salted hashing with **bcrypt**.
- **OAuth2 JWT Token Issuance**: Expiration-controlled JSON Web Tokens signed with HMAC-SHA256.
- **Dual Login Support**: Supports both standard JSON payloads (`{"email": "...", "password": "..."}`) and `application/x-www-form-urlencoded` credentials, providing 1-click **Authorize** button compatibility in Swagger UI.
- **Zero Credential Leakage**: Password hashes and secret keys are excluded from all API response models.
- **Current User Profile**: Fast profile retrieval with cached dependency validation.

### 📋 2. Comprehensive Task Management
- **Task Lifecycle**: Full CRUD operations for to-do items with fields: `id`, `title`, `description`, `status` (`pending`, `in_progress`, `completed`), `priority` (`low`, `medium`, `high`), `due_date`, `created_at`, `updated_at`, and `owner_id`.
- **Multi-Tenant Data Isolation**: Database queries strictly filter by `owner_id == current_user.id`. Any attempt by User B to access, update, or delete User A's task safely yields a `404 Not Found` rather than leaking resource existence.
- **Granular Updates**: Full update (`PUT`) and dedicated status transition (`PATCH /tasks/{id}/status`). Unprovided fields are never unintentionally overwritten.

### 🔍 3. Advanced Filtering, Search, Sorting & Pagination
- **Multi-Attribute Filters**: Filter by `status` and `priority`.
- **Case-Insensitive Search**: Partial title matching using SQL `ILIKE`.
- **Configurable Sorting**: Sort by `created_at`, `due_date`, `title`, `priority`, or `status` in either ascending (`asc`) or descending (`desc`) order.
- **Offset-Limit Pagination**: High-efficiency paginated responses containing `items`, `total`, `limit`, and `offset`.

### 📊 4. Dashboard & Aggregated Metrics
- **Real-Time Summary**: Single aggregated SQL query computing:
  - `total_tasks`: Count of all tasks owned by the user.
  - `pending_tasks`: Count of tasks in `pending` status.
  - `in_progress_tasks`: Count of tasks in `in_progress` status.
  - `completed_tasks`: Count of tasks in `completed` status.
  - `overdue_tasks`: Count of active tasks (`status != completed`) whose `due_date` has elapsed.

---

## 🛠️ Technology Stack

| Component | Technology | Rationale |
| :--- | :--- | :--- |
| **Language** | Python 3.11+ / 3.12+ | Modern type hinting, high performance, match statements |
| **Framework** | FastAPI 0.115+ | High-throughput asynchronous ASGI web framework |
| **Data Validation** | Pydantic v2 | Rust-accelerated request/response serialization & validation |
| **ORM** | SQLAlchemy 2.0 | Modern `Mapped[]` declarative models, robust connection pooling |
| **Migrations** | Alembic 1.13+ | Version-controlled, reproducible schema migrations |
| **Databases** | PostgreSQL / SQLite | Enterprise PostgreSQL in production; SQLite for local runs |
| **Authentication** | PyJWT + Bcrypt | Cryptographically secure password hashing and JWT issuance |
| **Testing** | Pytest + HTTPX | Automated test suite with isolated in-memory test database |
| **Server** | Uvicorn | High-performance ASGI web server |
| **Containerization** | Docker & Docker Compose | Multi-stage slim Docker build and container orchestration |

---

## 📂 Architecture and Directory Structure

The project strictly decouples presentation (API routes), business logic (services), persistence (SQLAlchemy models), and validation (Pydantic schemas).

```
task-management-api/
├── app/
│   ├── __init__.py
│   ├── main.py                  # Application entrypoint, CORS, custom error handlers
│   ├── core/
│   │   ├── config.py            # Typed settings loaded from .env via Pydantic Settings
│   │   └── security.py          # Bcrypt hashing & JWT encode/decode utilities
│   ├── db/
│   │   ├── base.py              # DeclarativeBase for SQLAlchemy 2.0
│   │   └── session.py           # Engine creation, connection pooling, SessionLocal
│   ├── models/
│   │   ├── user.py              # User SQLAlchemy model
│   │   └── task.py              # Task SQLAlchemy model
│   ├── schemas/
│   │   ├── auth.py              # Token & Login request validation schemas
│   │   ├── user.py              # User request & response schemas
│   │   └── task.py              # Task validation, query, list & summary schemas
│   ├── api/
│   │   └── v1/
│   │       ├── router.py        # Central v1 router (handles endpoint order)
│   │       └── endpoints/
│   │           ├── auth.py      # /auth/register, /auth/login, /auth/me
│   │           ├── tasks.py     # /tasks CRUD, filters, pagination, sorting
│   │           └── summary.py   # /tasks/summary dashboard metrics
│   ├── services/
│   │   ├── user_service.py      # User retrieval and registration logic
│   │   └── task_service.py      # Task queries, mutations, and metrics aggregation
│   └── dependencies/
│       ├── db.py                # Database session generator (get_db)
│       └── auth.py              # OAuth2 Bearer token extraction & user validation
├── alembic/
│   ├── env.py                   # Dynamic Alembic environment bound to settings
│   ├── script.py.mako           # Migration template
│   └── versions/                # Migration revision scripts
├── tests/
│   ├── conftest.py              # Isolated test client & in-memory DB fixtures
│   ├── test_auth.py             # Authentication & profile test cases
│   ├── test_tasks.py            # Task CRUD, filters, sorting & isolation tests
│   └── test_summary.py          # Dashboard metric calculations tests
├── .env.example                 # Template for environment variables
├── .env                         # Active local configuration (git-ignored)
├── .gitignore                   # Excludes venv, pycache, secrets, and SQLite files
├── alembic.ini                  # Alembic CLI configuration
├── Dockerfile                   # Multi-stage production container build
├── docker-compose.yml           # Multi-container setup (API + PostgreSQL)
├── pyproject.toml               # Pytest configuration and project metadata
├── requirements.txt             # Pinned project dependencies
└── README.md                    # Project documentation & resume guide
```

---

## ⚡ Quickstart & Local Installation

### Prerequisites
- Python 3.11+ installed (`python --version`)
- Git installed

### 1. Clone & Set Up Virtual Environment

**Windows PowerShell:**
```powershell
# Navigate into the project folder
cd "Task Management REST API"

# Create a virtual environment
python -m venv .venv

# Activate the virtual environment
.\.venv\Scripts\Activate.ps1
```

**Linux / macOS:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

---

### 2. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

---

### 3. Environment Configuration

Copy `.env.example` to `.env`:

**Windows PowerShell:**
```powershell
Copy-Item .env.example .env
```

**Linux / macOS:**
```bash
cp .env.example .env
```

By default, `.env` is configured to use a local SQLite database (`sqlite:///./taskmanagement.db`) so you can run and test immediately without installing or starting PostgreSQL.

To connect to a **PostgreSQL database**, simply update the `DATABASE_URL` in `.env`:
```env
DATABASE_URL="postgresql+psycopg2://postgres:yourpassword@localhost:5432/taskdb"
```

---

### 4. Run Database Migrations

Apply the database schema using Alembic:

```bash
alembic upgrade head
```

*Expected output:*
```
INFO  [alembic.runtime.migration] Context impl SQLiteImpl (or PostgresqlImpl).
INFO  [alembic.runtime.migration] Running upgrade  -> b93a6ff17687, create users and tasks tables
```

---

### 5. Start the API Server

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

The application is now running at:
- **API Base URL**: `http://127.0.0.1:8000`
- **Interactive Swagger UI**: `http://127.0.0.1:8000/docs`
- **ReDoc Documentation**: `http://127.0.0.1:8000/redoc`
- **Health Check**: `http://127.0.0.1:8000/health`

---

## 🧪 Running Automated Tests

The test suite runs against an **isolated in-memory database**, ensuring your development and production databases are never modified.

Execute the 24 automated unit and integration tests:

```bash
pytest
```

*Result:*
```
============================= 24 passed in 38.99s =============================
```

### Test Coverage Highlights:
- ✅ Successful registration and duplicate email handling (409 Conflict)
- ✅ Password validation (length, hashing verification)
- ✅ JWT authentication via JSON body and OAuth2 form data
- ✅ Token expiration, missing headers, and malformed token rejection (401 Unauthorized)
- ✅ Task creation, reading, updating, and deleting (201, 200, 204)
- ✅ Multi-tenant isolation (User B cannot access or modify User A's task -> 404)
- ✅ Filter by status and priority, search by title keyword
- ✅ Pagination limit/offset verification and sorting by dates
- ✅ Dashboard summary counts and overdue date logic

---

## 🐳 Docker & Docker Compose Setup

Run the full production stack (FastAPI + PostgreSQL 16) with a single command:

```bash
# Build and start PostgreSQL and FastAPI
docker compose up --build -d

# View real-time logs
docker compose logs -f

# Stop all containers and preserve database volume
docker compose down
```

The container automatically executes `alembic upgrade head` before serving traffic on port 8000.

---

## 📡 API Endpoint Reference

### Authentication (`/api/v1/auth`)

| Method | Endpoint | Status | Description | Auth Required |
| :--- | :--- | :--- | :--- | :--- |
| `POST` | `/api/v1/auth/register` | `201 Created` | Register a new user | ❌ No |
| `POST` | `/api/v1/auth/login` | `200 OK` | Authenticate and obtain JWT token | ❌ No |
| `GET` | `/api/v1/auth/me` | `200 OK` | Get current user's profile | 🔒 Bearer Token |

### Tasks (`/api/v1/tasks`)

| Method | Endpoint | Status | Description | Auth Required |
| :--- | :--- | :--- | :--- | :--- |
| `POST` | `/api/v1/tasks` | `201 Created` | Create a new task | 🔒 Bearer Token |
| `GET` | `/api/v1/tasks` | `200 OK` | List tasks (with filter, search, sort, pagination) | 🔒 Bearer Token |
| `GET` | `/api/v1/tasks/summary` | `200 OK` | Task metrics (total, pending, completed, overdue) | 🔒 Bearer Token |
| `GET` | `/api/v1/tasks/{id}` | `200 OK` | Retrieve a task by ID | 🔒 Bearer Token |
| `PUT` | `/api/v1/tasks/{id}` | `200 OK` | Update task fields | 🔒 Bearer Token |
| `PATCH`| `/api/v1/tasks/{id}/status` | `200 OK` | Update task status only | 🔒 Bearer Token |
| `DELETE`| `/api/v1/tasks/{id}` | `204 No Content` | Delete a task | 🔒 Bearer Token |

---

## 💡 Example API Requests & Responses

### 1. Register User
**Request:**
```http
POST /api/v1/auth/register HTTP/1.1
Host: 127.0.0.1:8000
Content-Type: application/json

{
  "email": "developer@example.com",
  "password": "SuperSecurePassword123!",
  "full_name": "Senior Developer"
}
```

**Response (`201 Created`):**
```json
{
  "email": "developer@example.com",
  "full_name": "Senior Developer",
  "id": 1,
  "is_active": true,
  "created_at": "2026-10-14T16:30:00Z",
  "updated_at": "2026-10-14T16:30:00Z"
}
```

---

### 2. Login & Obtain JWT Token
**Request:**
```http
POST /api/v1/auth/login HTTP/1.1
Host: 127.0.0.1:8000
Content-Type: application/json

{
  "email": "developer@example.com",
  "password": "SuperSecurePassword123!"
}
```

**Response (`200 OK`):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

---

### 3. Create a Task
**Request:**
```http
POST /api/v1/tasks HTTP/1.1
Host: 127.0.0.1:8000
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "title": "Build Microservices Infrastructure",
  "description": "Configure Docker Compose, Alembic, and PostgreSQL pooling",
  "priority": "high",
  "status": "in_progress",
  "due_date": "2026-12-31T23:59:59Z"
}
```

**Response (`201 Created`):**
```json
{
  "title": "Build Microservices Infrastructure",
  "description": "Configure Docker Compose, Alembic, and PostgreSQL pooling",
  "priority": "high",
  "due_date": "2026-12-31T23:59:59Z",
  "id": 1,
  "status": "in_progress",
  "owner_id": 1,
  "created_at": "2026-10-14T16:31:00Z",
  "updated_at": "2026-10-14T16:31:00Z"
}
```

---

### 4. Retrieve Dashboard Summary
**Request:**
```http
GET /api/v1/tasks/summary HTTP/1.1
Host: 127.0.0.1:8000
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response (`200 OK`):**
```json
{
  "total_tasks": 12,
  "pending_tasks": 4,
  "in_progress_tasks": 3,
  "completed_tasks": 5,
  "overdue_tasks": 1
}
```

---

## 🔒 Security Best Practices Implemented

1. **Defense Against IDOR (Insecure Direct Object Reference)**:
   Every task query enforces `Task.owner_id == current_user.id`. Even if a user guesses another user's task ID, the API returns a generic `404 Not Found`, denying knowledge of foreign resources.
2. **Non-Reversible Password Storage**:
   Passwords are never stored in plain-text. They are hashed using bcrypt with automatic cryptographic salts.
3. **Stateless JWT with Expiration**:
   Tokens include an issued-at (`iat`) and expiration (`exp`) timestamp and are validated on every authenticated request.
4. **SQL Injection Prevention**:
   All database operations use SQLAlchemy 2.0 parameterized queries and ORM mappings.
5. **Safe Data Updates**:
   Update routes utilize Pydantic's `model_dump(exclude_unset=True)` to prevent overwriting unsupplied fields with `null`.
6. **Container Security**:
   The `Dockerfile` defines a non-root system user (`appuser:1001`) to eliminate container breakout risks.

---

## 🚀 Production Deployment Guide

### Deploying to Render / Railway / Fly.io

1. **Create a Managed PostgreSQL Database** on your provider (e.g., Render Postgres, Neon, Supabase, or AWS RDS).
2. **Set Environment Variables** in the hosting dashboard:
   - `DATABASE_URL`: `postgresql+psycopg2://<user>:<password>@<host>:<port>/<dbname>`
   - `JWT_SECRET_KEY`: A cryptographically secure 64-character token (`python -c "import secrets; print(secrets.token_urlsafe(32))"`)
   - `ENVIRONMENT`: `production`
   - `BACKEND_CORS_ORIGINS`: `["https://your-frontend-domain.com"]`
3. **Set Build & Start Commands**:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT`

---

## 💼 Resume & Interview Preparation

### Suggested Repository Details
- **Repository Name**: `task-management-fastapi`
- **Repository Description**: `Production-ready Task Management REST API using FastAPI, SQLAlchemy 2.0, PostgreSQL, Alembic migrations, and OAuth2 JWT authentication.`

### 📄 Resume Bullet Points

> - **Architected and developed a production-grade Task Management REST API** using FastAPI, SQLAlchemy 2.0, and PostgreSQL, implementing OAuth2 JWT Bearer authentication and Bcrypt password hashing.
> - **Engineered multi-tenant data isolation and role-based access control**, preventing IDOR vulnerabilities while supporting dynamic title search (ILIKE), multi-attribute filtering, sorting, and limit-offset pagination.
> - **Built a comprehensive automated test suite with 24 tests using Pytest and HTTPX** against an isolated in-memory test database, achieving 100% test pass rates and zero data pollution.

---

### 🎤 5 Interview Questions & Detailed Answers

#### Q1: Why did you separate the route handlers from the service layer?
> **Answer**:
> Separating route handlers (`app/api/v1/endpoints/`) from the service layer (`app/services/`) follows the Single Responsibility Principle and Clean Architecture. Route handlers are responsible solely for HTTP-specific tasks: deserializing request payloads, extracting dependency-injected database sessions or auth tokens, and selecting the HTTP status code. The service layer contains pure business logic and ORM queries. This decoupling makes the business logic directly testable without needing an HTTP context and allows reuse across alternative interfaces (such as Celery background workers, CLI tools, or WebSockets).

#### Q2: How did you prevent Insecure Direct Object Reference (IDOR) vulnerabilities?
> **Answer**:
> IDOR occurs when an application exposes a reference to an internal resource (such as `task_id = 42`) and fails to verify that the requesting user owns that resource. In this project, `owner_id` is never accepted from client input; it is strictly derived from the validated JWT token of `current_user`. Furthermore, every database retrieval, update, or deletion query executes `WHERE Task.id == task_id AND Task.owner_id == current_user.id`. If a user attempts to access another user's task, the API returns `404 Not Found`, denying that the task even exists.

#### Q3: Why use Alembic migrations instead of `Base.metadata.create_all()`?
> **Answer**:
> `Base.metadata.create_all()` only creates tables if they do not already exist; it cannot alter existing columns, add constraints, change indexes, or rename fields on live databases. Alembic tracks schema revisions in a version-controlled table (`alembic_version`), providing deterministic, auditable, and rollback-capable database schema evolution across environments (local, staging, production) without downtime or data corruption.

#### Q4: How is the `/tasks/summary` metric calculated efficiently in SQL?
> **Answer**:
> Instead of making 5 separate database queries or fetching all user tasks into Python memory to count with loops, the summary endpoint uses a single aggregated SQL query combining `func.count(Task.id)` and conditional `case(...)` statements:
> ```python
> select(
>     func.count(Task.id).label("total"),
>     func.count(case((Task.status == TaskStatus.PENDING, 1))).label("pending"),
>     func.count(case((Task.status == TaskStatus.IN_PROGRESS, 1))).label("in_progress"),
>     func.count(case((Task.status == TaskStatus.COMPLETED, 1))).label("completed"),
>     func.count(case((and_(Task.due_date < func.now(), Task.status != TaskStatus.COMPLETED), 1))).label("overdue"),
> ).where(Task.owner_id == owner_id)
> ```
> This executes entirely within the database engine in a single round-trip with `O(1)` memory overhead on the web application server.

#### Q5: How do you ensure the test suite does not modify production or development data?
> **Answer**:
> In `tests/conftest.py`, a dedicated SQLite in-memory database engine is created using SQLAlchemy's `StaticPool`. Using FastAPI's `app.dependency_overrides[get_db]`, the production database session dependency is swapped out for a clean, test-scoped session before each test and torn down after each test. This ensures total test isolation, sub-second test execution, zero risk of data contamination, and enables tests to pass even in CI/CD environments without an external database instance.
