# AI Resume-Based Interview & Skill Gap Platform

A production-ready AI-powered platform for conducting adaptive technical interviews, skill gap analysis, and personalized learning roadmaps.

## Features

### Core Functionality
- ✅ Secure user registration and JWT authentication
- ✅ Resume upload (PDF/DOC/DOCX) with parsing
- ✅ Structured profile extraction (skills, experience, projects, education)
- ✅ Job role selection and JD analysis
- ✅ Adaptive interview engine with dynamic follow-ups
- ✅ Multi-dimensional answer evaluation
- ✅ Resume claim validation
- ✅ Skill gap detection and analysis
- ✅ Personalized improvement roadmaps
- ✅ Comprehensive interview reports
- ✅ Interview history and progress tracking
- ✅ Admin panel with RBAC

### Technical Features
- Provider-independent AI Gateway (OpenAI, Anthropic, Mock)
- Modular service architecture
- PostgreSQL with proper relational design
- Redis caching and Celery background tasks
- Secure file storage with access control
- Rate limiting and security hardening
- Comprehensive test coverage

## Architecture

```
frontend/           - HTML/CSS/JS responsive UI
backend/
  app/
    api/           - FastAPI route handlers
    core/          - Configuration and dependencies
    models/        - SQLAlchemy database models
    schemas/       - Pydantic validation schemas
    services/      - Business logic layer
    repositories/  - Data access layer
    ai/            - AI Gateway and providers
    workers/       - Celery background tasks
    security/      - Authentication and authorization
    utils/         - Helper functions
  main.py          - Application entry point
storage/           - Resume and file storage
tests/             - Comprehensive test suite
docker/            - Docker configuration
```

## Prerequisites

- Python 3.11+
- PostgreSQL 14+
- Redis 7+
- Docker & Docker Compose (recommended)

## Installation

### Using Docker (Recommended)

1. Clone the repository
2. Copy environment template:
```bash
cp .env.example .env
```

3. Configure environment variables in `.env`:
```env
# Database
DATABASE_URL=postgresql://postgres:postgres@db:5432/interview_platform
DATABASE_URL_TEST=postgresql://postgres:postgres@db:5432/interview_platform_test

# Redis
REDIS_URL=redis://redis:6379/0

# Security
SECRET_KEY=your-secret-key-here-min-32-chars
JWT_SECRET_KEY=your-jwt-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# AI Provider
AI_PROVIDER=mock  # Options: openai, anthropic, mock
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# Storage
STORAGE_PATH=./storage
MAX_FILE_SIZE_MB=10

# Application
ENVIRONMENT=development
DEBUG=true
CORS_ORIGINS=["http://localhost:3000","http://localhost:8000"]
```

4. Start services:
```bash
docker-compose up -d
```

5. Run migrations:
```bash
docker-compose exec backend alembic upgrade head
```

6. Access the application:
- Frontend: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Admin Panel: http://localhost:8000/admin

### Manual Installation

1. Install Python dependencies:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. Install PostgreSQL and Redis locally

3. Configure `.env` file with local connection strings

4. Run migrations:
```bash
alembic upgrade head
```

5. Start backend:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

6. Start Celery worker:
```bash
celery -A app.workers.celery_app worker --loglevel=info
```

## Database Setup

### Create Database
```sql
CREATE DATABASE interview_platform;
CREATE DATABASE interview_platform_test;
```

### Run Migrations
```bash
# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

## Running Tests

### All Tests
```bash
pytest
```

### Specific Test Categories
```bash
# Unit tests
pytest tests/unit/

# API tests
pytest tests/api/

# Security tests
pytest tests/security/

# With coverage
pytest --cov=app --cov-report=html
```

### E2E Tests
```bash
pytest tests/e2e/ -v
```

## API Documentation

### Authentication
```
POST /api/auth/register        - Register new user
POST /api/auth/login           - Login user
POST /api/auth/logout          - Logout user
GET  /api/auth/me              - Get current user
```

### Resumes
```
POST   /api/resumes            - Upload resume
GET    /api/resumes            - List user resumes
GET    /api/resumes/{id}       - Get resume details
DELETE /api/resumes/{id}       - Delete resume
PATCH  /api/resumes/{id}/profile - Update extracted profile
```

### Job Descriptions
```
GET  /api/job-roles            - List available job roles
POST /api/job-descriptions     - Upload/analyze JD
GET  /api/job-descriptions/{id} - Get JD details
```

### Interviews
```
POST   /api/interviews         - Create interview
GET    /api/interviews         - List user interviews
GET    /api/interviews/{id}    - Get interview details
POST   /api/interviews/{id}/start - Start interview
POST   /api/interviews/{id}/answer - Submit answer
POST   /api/interviews/{id}/finish - Finish interview
GET    /api/interviews/{id}/report - Get final report
GET    /api/interviews/{id}/skill-gaps - Get skill gap analysis
GET    /api/interviews/{id}/roadmap - Get improvement roadmap
```

### Dashboard & Analytics
```
GET /api/dashboard             - User dashboard data
GET /api/progress              - Progress tracking
GET /api/history               - Interview history
```

### Admin (Requires admin role)
```
GET    /api/admin/users        - List all users
GET    /api/admin/interviews   - List all interviews
GET    /api/admin/analytics    - System analytics
GET    /api/admin/audit-logs   - Audit logs
```

## AI Provider Configuration

### Mock Provider (Default for Development)
```env
AI_PROVIDER=mock
```
Returns realistic test responses without API calls.

### OpenAI
```env
AI_PROVIDER=openai
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4
```

### Anthropic
```env
AI_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-...
ANTHROPIC_MODEL=claude-3-sonnet-20240229
```

## Production Deployment

### Render Backend and Vercel Frontend

The repository includes `render.yaml` for the FastAPI service, PostgreSQL, and
Redis. In Render, create a Blueprint from this repository and set the
`CORS_ORIGINS` environment variable to the deployed Vercel URL, for example:

```env
CORS_ORIGINS=["https://your-app.vercel.app"]
```

The Blueprint sets `PYTHON_VERSION=3.11.9` and runs `alembic upgrade head`
before starting the service. This keeps the locked Pydantic dependencies on a
Python version with published wheels instead of attempting a Rust build in
Render's build environment. If configuring the service manually, set the same
`PYTHON_VERSION` environment variable and use the `backend` root directory.

For Vercel, create a project with `frontend` as its Root Directory and deploy
it as a static site. Before deploying, replace the placeholder URL in
`frontend/config.js` with the public Render backend URL:

```js
API_BASE_URL: 'https://your-api.onrender.com'
```

The frontend appends `/api` automatically. Deploy the frontend after the
backend so its Vercel URL can be added to Render's `CORS_ORIGINS` setting.

### Docker Production Build
```bash
docker build -f docker/Dockerfile.prod -t interview-platform:latest .
```

### Environment Variables (Production)
```env
ENVIRONMENT=production
DEBUG=false
DATABASE_URL=postgresql://user:pass@host:5432/db
REDIS_URL=redis://host:6379/0
SECRET_KEY=<strong-random-key>
JWT_SECRET_KEY=<strong-random-key>
AI_PROVIDER=openai
OPENAI_API_KEY=<production-key>
STORAGE_PATH=/app/storage
CORS_ORIGINS=["https://yourdomain.com"]
```

### Security Checklist
- [ ] Change all default secrets
- [ ] Use HTTPS with valid SSL certificates
- [ ] Configure firewall rules
- [ ] Set up database backups
- [ ] Configure log aggregation
- [ ] Enable rate limiting
- [ ] Set up monitoring and alerts
- [ ] Configure CORS properly
- [ ] Use strong JWT secrets
- [ ] Enable audit logging

## Troubleshooting

### Database Connection Issues
```bash
# Check PostgreSQL is running
docker-compose ps db

# Check logs
docker-compose logs db

# Reset database
docker-compose down -v
docker-compose up -d db
alembic upgrade head
```

### Redis Connection Issues
```bash
# Check Redis is running
docker-compose ps redis

# Test connection
redis-cli -h localhost -p 6379 ping
```

### Resume Parsing Issues
- Ensure file is valid PDF/DOC/DOCX
- Check file size < 10MB
- Verify AI provider is configured
- Check backend logs for details

### Interview Not Generating Questions
- Verify resume profile is complete
- Check AI provider API key is valid
- Check rate limits
- Review backend logs

### Tests Failing
```bash
# Run with verbose output
pytest -v -s

# Run specific test
pytest tests/api/test_auth.py::test_register -v

# Check test database
psql -d interview_platform_test -U postgres
```

## Performance Optimization

### Caching
- Resume parsing results cached in Redis
- Job role data cached for 1 hour
- Interview state cached during active sessions

### Database Indexing
- Indexed on user_id, resume_id, interview_id
- Composite indexes on frequently queried combinations
- Full-text search on skills and descriptions

### AI Cost Control
- Token limits per request
- Compact interview state representation
- Caching of repeated analyses
- Smart model routing (cheaper models for simpler tasks)

## Security Features

- JWT-based authentication with refresh tokens
- Password hashing with bcrypt
- Role-based access control (User, Admin)
- Rate limiting on all endpoints
- Input validation with Pydantic
- SQL injection protection via SQLAlchemy
- XSS protection with content security policies
- CORS configuration
- Secure file upload validation
- Private file storage with signed access
- Audit logging of sensitive operations
- Secret management via environment variables

## License

Proprietary - All rights reserved

## Support

For issues and questions, contact support@interviewplatform.com
