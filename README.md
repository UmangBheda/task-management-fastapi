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

d torn down after each test. This ensures total test isolation, sub-second test execution, zero risk of data contamination, and enables tests to pass even in CI/CD environments without an external database instance.
