# Testing Guide

## Overview

This document provides comprehensive testing instructions for the AI Resume-Based Interview & Skill Gap Platform.

## Test Structure

```
tests/
├── conftest.py           # Test fixtures and configuration
├── test_auth_api.py      # Authentication endpoint tests
├── test_resumes_api.py   # Resume upload/management tests
├── test_jobs_api.py      # Job roles and JD tests
├── test_interviews_api.py # Interview workflow tests
├── test_services.py      # Service layer tests
├── test_security.py      # Security function tests
└── test_ai_gateway.py    # AI provider tests
```

## Running Tests

### Prerequisites

```bash
# Install test dependencies
pip install pytest pytest-asyncio pytest-cov httpx faker

# Set up test database
createdb interview_platform_test

# Configure test environment
cp .env.example .env
# Edit .env and set DATABASE_URL_TEST
```

### Run All Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_auth_api.py

# Run specific test
pytest tests/test_auth_api.py::test_register_user
```

### Test Categories

```bash
# Unit tests only
pytest -m "not integration"

# Integration tests only
pytest -m integration

# Fast tests only
pytest -m "not slow"
```

## Test Coverage

### Authentication Tests

- User registration
- Login with valid/invalid credentials
- Token generation and validation
- Access control and authorization
- Password hashing security

### Resume Tests

- Resume upload (PDF/DOCX)
- File validation (size, type)
- Resume parsing
- Profile extraction
- CRUD operations

### Interview Tests

- Interview creation
- Adaptive question generation
- Answer submission and evaluation
- Follow-up question generation
- Interview completion
- State management

### Job Tests

- Job role listing
- Job description upload
- JD parsing and analysis
- Skill extraction

### Service Layer Tests

- Resume parser functionality
- AI gateway with mock provider
- Skill gap analyzer
- Roadmap generator
- Report generator

### Security Tests

- Password hashing
- JWT token creation/validation
- Access control enforcement
- Input validation
- SQL injection prevention
- XSS protection

## Manual Testing Checklist

### Registration & Authentication
- [ ] Register new user with valid data
- [ ] Register with existing email (should fail)
- [ ] Login with correct credentials
- [ ] Login with wrong password (should fail)
- [ ] Access protected endpoint without token (should fail)
- [ ] Logout successfully

### Resume Upload & Parsing
- [ ] Upload PDF resume
- [ ] Upload DOCX resume
- [ ] Upload invalid file type (should fail)
- [ ] Upload oversized file (should fail)
- [ ] View parsed candidate profile
- [ ] Edit candidate profile
- [ ] Delete resume

### Job Selection
- [ ] List available job roles
- [ ] Select predefined job role
- [ ] Upload custom job description
- [ ] Parse job requirements

### Interview Flow
- [ ] Create interview with resume and job role
- [ ] Start interview and receive first question
- [ ] Submit answer
- [ ] Receive next question
- [ ] Verify adaptive difficulty
- [ ] Verify no duplicate questions
- [ ] Verify follow-up questions
- [ ] Complete interview
- [ ] End interview early

### Interview Results
- [ ] View interview report
- [ ] Check overall score
- [ ] Check category scores (technical, project, etc.)
- [ ] View strengths
- [ ] View weaknesses
- [ ] View skill gap analysis
- [ ] View improvement roadmap
- [ ] Verify resume claim validation

### Dashboard & History
- [ ] View dashboard statistics
- [ ] View recent interviews
- [ ] View top strengths
- [ ] View priority gaps
- [ ] View interview history
- [ ] View progress trends

## E2E Test Scenarios

### Complete User Journey

1. **Registration**
   ```
   POST /api/auth/register
   {
     "email": "test@example.com",
     "password": "password123",
     "full_name": "Test User"
   }
   Expected: 201, returns token and user
   ```

2. **Upload Resume**
   ```
   POST /api/resumes
   File: sample_resume.pdf
   Expected: 201, resume uploaded and parsed
   ```

3. **Create Interview**
   ```
   POST /api/interviews
   {
     "resume_id": 1,
     "job_role_id": 1,
     "difficulty": "intermediate"
   }
   Expected: 201, interview created
   ```

4. **Start Interview**
   ```
   POST /api/interviews/1/start
   Expected: 200, returns first question
   ```

5. **Submit Multiple Answers**
   ```
   POST /api/interviews/1/answer
   {
     "answer_text": "Detailed answer..."
   }
   Expected: 200, returns next question
   Repeat 10-15 times
   ```

6. **Complete Interview**
   ```
   POST /api/interviews/1/finish
   Expected: 200, interview marked complete
   ```

7. **Get Results**
   ```
   GET /api/interviews/1/report
   GET /api/interviews/1/skill-gaps
   GET /api/interviews/1/roadmap
   Expected: 200, comprehensive results
   ```

## Security Testing

### SQL Injection Tests

```bash
# Test with SQL injection payloads
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin'\'' OR 1=1--", "password": "test"}'

Expected: 401, not successful injection
```

### XSS Tests

```bash
# Test with XSS payload in resume
Upload resume with: <script>alert('XSS')</script>

Expected: Sanitized or escaped output
```

### Authentication Bypass Tests

```bash
# Access protected endpoint without token
curl http://localhost:8000/api/dashboard

Expected: 403 Unauthorized
```

### IDOR Tests

```bash
# Try to access another user's resume
GET /api/resumes/{other_user_resume_id}

Expected: 403 Forbidden
```

## Performance Testing

### Load Test with pytest-benchmark

```python
def test_question_generation_performance(benchmark):
    result = benchmark(generate_question, context)
    assert result is not None
```

### Concurrent User Test

```bash
# Use locust or k6 for load testing
locust -f locustfile.py --host=http://localhost:8000
```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov
      
      - name: Run tests
        run: pytest --cov=app --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

## Troubleshooting

### Test Database Connection Issues

```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# Create test database
createdb interview_platform_test

# Verify connection
psql -d interview_platform_test -c "SELECT 1"
```

### Mock Provider Not Working

```bash
# Ensure AI_PROVIDER is set to 'mock' in .env
echo "AI_PROVIDER=mock" >> .env
```

### Import Errors

```bash
# Ensure you're in the backend directory
cd backend

# Run tests with Python path
PYTHONPATH=. pytest
```

## Coverage Goals

- **Overall**: > 80%
- **Critical paths** (auth, interview engine): > 90%
- **API endpoints**: 100%
- **Business logic**: > 85%

## Test Maintenance

- Review and update tests with each feature change
- Add tests for bug fixes
- Keep test data realistic
- Mock external dependencies
- Use fixtures for common setup
- Clean up test database after each run
