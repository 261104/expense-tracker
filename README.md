# Expense Tracker

A full-stack personal finance application for tracking expenses, managing budgets, and viewing spending insights.

Built as a portfolio project to demonstrate production-oriented **Python/FastAPI backend development, React frontend development, PostgreSQL, authentication, database migrations, automated testing, and Docker-based deployment**.

## Features

* User registration and JWT authentication
* Argon2 password hashing
* User-scoped expense management
* Create, read, update, and delete expenses
* Pagination and safe sorting
* Category and date filtering
* Minimum and maximum amount filtering
* Spending statistics and category breakdowns
* Monthly and category budgets
* Dashboard aggregation
* PostgreSQL database
* Alembic database migrations
* Input validation with Pydantic
* Protected API endpoints with ownership enforcement
* Responsive React dashboard
* Loading, error, and empty states
* Backend tests with pytest
* Frontend behavior tests with Vitest and React Testing Library
* Docker Compose development environment
* GitHub Actions CI

## Tech Stack

### Backend

* Python
* FastAPI
* SQLAlchemy 2.x
* Pydantic
* PostgreSQL
* Psycopg
* Alembic
* PyJWT
* Argon2

### Frontend

* React
* Vite
* React Router
* JavaScript
* CSS

### Testing & DevOps

* pytest
* Vitest
* React Testing Library
* Docker
* Docker Compose
* GitHub Actions
* Nginx

## Architecture

```text
                    ┌─────────────────────┐
                    │    React + Vite     │
                    │      Frontend       │
                    └──────────┬──────────┘
                               │ HTTP/JSON
                               ▼
                    ┌─────────────────────┐
                    │    FastAPI REST     │
                    │        API          │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │ Authentication /    │
                    │   Dependencies      │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │      Routers        │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │      Services       │
                    │ Business / DB Logic │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │    SQLAlchemy ORM   │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │     PostgreSQL      │
                    └─────────────────────┘
```

## Project Structure

```text
expense-tracker/
│
├── backend/
│   ├── app/
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   └── security.py
│   │   │
│   │   ├── database/
│   │   │   ├── base.py
│   │   │   └── connection.py
│   │   │
│   │   ├── models/
│   │   │   ├── user.py
│   │   │   ├── expense.py
│   │   │   └── budget.py
│   │   │
│   │   ├── schemas/
│   │   │   ├── auth.py
│   │   │   ├── user.py
│   │   │   ├── expense.py
│   │   │   └── budget.py
│   │   │
│   │   ├── routers/
│   │   │   ├── auth.py
│   │   │   ├── expenses.py
│   │   │   └── dashboard.py
│   │   │
│   │   ├── services/
│   │   │   ├── auth.py
│   │   │   ├── expenses.py
│   │   │   └── dashboard.py
│   │   │
│   │   ├── dependencies.py
│   │   └── main.py
│   │
│   ├── alembic/
│   │   └── versions/
│   │
│   ├── tests/
│   ├── Dockerfile
│   ├── alembic.ini
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── App.css
│   │   ├── index.css
│   │   └── main.jsx
│   │
│   ├── public/
│   ├── Dockerfile
│   ├── nginx.conf
│   ├── package.json
│   └── vite.config.js
│
├── .github/
│   └── workflows/
│       └── ci.yml
│
├── docker-compose.yml
├── .env.example
├── .gitignore
└── README.md
```

## API Endpoints

### Authentication

| Method | Endpoint         | Description                    |
| ------ | ---------------- | ------------------------------ |
| POST   | `/auth/register` | Register a new user            |
| POST   | `/auth/login`    | Authenticate and receive a JWT |

### Expenses

| Method | Endpoint          | Description                        |
| ------ | ----------------- | ---------------------------------- |
| GET    | `/expenses`       | List authenticated user's expenses |
| POST   | `/expenses`       | Create an expense                  |
| GET    | `/expenses/{id}`  | Get an expense                     |
| PUT    | `/expenses/{id}`  | Update an expense                  |
| DELETE | `/expenses/{id}`  | Delete an expense                  |
| GET    | `/expenses/stats` | Get spending statistics            |

Example:

```text
GET /expenses?page=1&limit=10&category=Food
```

### Budgets

| Method | Endpoint   | Description         |
| ------ | ---------- | ------------------- |
| GET    | `/budgets` | List user's budgets |
| POST   | `/budgets` | Create a budget     |

### Dashboard & Health

| Method | Endpoint     | Description                 |
| ------ | ------------ | --------------------------- |
| GET    | `/dashboard` | Get dashboard aggregation   |
| GET    | `/health`    | API health check            |
| GET    | `/health/db` | Database connectivity check |

All expense and budget operations are authenticated and scoped to the current user.

## Local Development

### Prerequisites

* Python 3.12+
* Node.js 20+
* PostgreSQL
* Git

### Backend Setup

From the project root:

```powershell
cd backend
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Create the local environment file:

```text
backend/.env
```

using:

```text
backend/.env.example
```

Configure your local PostgreSQL connection and JWT secret.

Run database migrations:

```powershell
python -m alembic -c alembic.ini upgrade head
```

Start the API:

```powershell
python -m uvicorn app.main:app --reload --port 8000
```

The API will be available at:

```text
http://localhost:8000
```

Interactive API documentation:

```text
http://localhost:8000/docs
```

OpenAPI schema:

```text
http://localhost:8000/openapi.json
```

### Frontend Setup

Open a second terminal:

```powershell
cd frontend
npm install
npm run dev
```

The frontend will normally be available at:

```text
http://localhost:5173
```

The frontend uses `VITE_API_URL` to determine the API base URL. The default development API is:

```text
http://localhost:8000
```

## Docker

Docker Compose runs the complete application stack:

```text
React / Nginx
      │
      ▼
FastAPI
      │
      ▼
PostgreSQL
```

Create the root environment file from:

```text
.env.example
```

Set:

```text
POSTGRES_PASSWORD=<your-local-password>
JWT_SECRET_KEY=<your-random-secret>
```

Then run:

```powershell
docker compose up --build
```

The default Docker endpoints are:

| Service     | Address                      |
| ----------- | ---------------------------- |
| Frontend    | `http://localhost:8080`      |
| Backend API | `http://localhost:8000`      |
| Swagger     | `http://localhost:8000/docs` |
| PostgreSQL  | `localhost:5434`             |

The PostgreSQL container uses host port **5434** to avoid conflicting with other local PostgreSQL services.

Secrets are provided through environment variables and are not baked into Docker images.

To stop the stack:

```powershell
docker compose down
```

The PostgreSQL data volume is retained unless explicitly removed.

## Database Migrations

Alembic manages database schema changes.

Apply all migrations:

```powershell
cd backend
python -m alembic -c alembic.ini upgrade head
```

Create a new migration after model changes:

```powershell
python -m alembic -c alembic.ini revision --autogenerate -m "describe change"
```

## Testing

### Backend

```powershell
cd backend
python -m pytest tests -q
```

Backend tests use an isolated SQLite database through FastAPI dependency overrides, so they do not modify the development PostgreSQL database.

### Frontend

```powershell
cd frontend
npm test
```

Build verification:

```powershell
npm run build
```

Frontend tests use Vitest, jsdom, and React Testing Library with mocked API calls.

## Continuous Integration

GitHub Actions runs automatically for pushes and pull requests targeting `main`.

The CI pipeline verifies:

```text
Backend
  ├── Install dependencies
  ├── Configure isolated test environment
  └── Run pytest

Frontend
  ├── Install dependencies
  └── Run production build
```

## Security

The application includes:

* JWT-based authentication
* Argon2 password hashing
* Protected routes
* User ownership enforcement
* Pydantic request validation
* Environment-based configuration
* Parameterized SQL through SQLAlchemy
* Short-lived access tokens
* CORS configuration
* No production secrets committed to Git

For production deployment, additional hardening should include HTTPS, managed PostgreSQL, a secret manager, restrictive CORS configuration, secure cookie-based sessions where appropriate, rate limiting, and a production reverse proxy.

## Production Considerations

This project is designed as a portfolio application while following production-oriented patterns.

For a production deployment:

1. Use managed PostgreSQL.
2. Store secrets in a dedicated secret manager.
3. Enable HTTPS.
4. Restrict `CORS_ORIGINS` to trusted domains.
5. Run Alembic migrations as part of the release process.
6. Add rate limiting and abuse protection.
7. Prefer secure `httpOnly` cookie-based authentication for higher-risk deployments.
8. Add refresh-token rotation if long-lived sessions are required.
9. Configure structured logging and application monitoring.
10. Use a production-grade reverse proxy.

## Learning & Engineering Focus

This project demonstrates practical full-stack engineering concepts including:

* REST API design
* Authentication and authorization
* JWT security
* Password hashing
* Dependency injection
* Service-layer architecture
* SQLAlchemy ORM
* PostgreSQL
* Database migrations
* API validation
* Pagination and filtering
* Aggregation queries
* Automated testing
* React state management
* API integration
* Docker containerization
* CI pipelines
* Environment-based configuration

## License

This project is intended as a portfolio and learning project.
