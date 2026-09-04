# AI Resume-Based Interview & Skill Gap Platform

## 🎯 Project Summary

A production-ready, full-stack AI-powered interview preparation platform that:

- Parses resumes and extracts structured candidate profiles
- Conducts adaptive, intelligent technical interviews
- Evaluates answers with multi-dimensional scoring
- Identifies skill gaps by comparing claimed vs demonstrated skills
- Generates personalized learning roadmaps
- Tracks progress across multiple interview attempts

**Built with:** FastAPI, PostgreSQL, Redis, React (vanilla JS), OpenAI/Anthropic AI

---

## ✨ Key Features Implemented

### Core Functionality
✅ User authentication with JWT (register, login, RBAC)  
✅ Resume upload (PDF/DOCX) with intelligent parsing  
✅ AI-powered profile extraction (skills, experience, projects, education)  
✅ Job role selection and custom job description upload  
✅ **Adaptive Interview Engine** - questions adjust based on previous answers  
✅ Multi-dimensional answer evaluation (correctness, depth, clarity, etc.)  
✅ Dynamic follow-up questions  
✅ Resume claim validation (claimed level vs demonstrated level)  
✅ Skill gap analysis with priority ranking  
✅ Personalized improvement roadmap generation  
✅ Comprehensive interview reports  
✅ Interview history and progress tracking  
✅ Dashboard with statistics and insights  

### Technical Features
✅ Provider-independent AI Gateway (OpenAI, Anthropic, Mock)  
✅ Modular service architecture (services, repositories, models)  
✅ PostgreSQL with proper relational design (15+ tables)  
✅ Redis caching for performance  
✅ Celery for background task processing  
✅ Secure file storage with validation  
✅ Rate limiting and security hardening  
✅ Comprehensive test suite (unit, integration, API)  
✅ Docker & Docker Compose setup  
✅ Alembic database migrations  
✅ Complete API documentation (OpenAPI/Swagger)  

---

## 📁 Project Structure

```
interview-platform/
├── backend/
│   ├── app/
│   │   ├── api/              # API route handlers
│   │   │   ├── auth.py
│   │   │   ├── resumes.py
│   │   │   ├── jobs.py
│   │   │   ├── interviews.py
│   │   │   ├── reports.py
│   │   │   └── dashboard.py
│   │   ├── core/             # Core configuration
│   │   │   ├── config.py
│   │   │   ├── database.py
│   │   │   └── redis.py
│   │   ├── models/           # SQLAlchemy models (15+ tables)
│   │   ├── schemas/          # Pydantic schemas
│   │   ├── services/         # Business logic
│   │   │   ├── resume_parser.py
│   │   │   ├── resume_analyzer.py
│   │   │   ├── job_analyzer.py
│   │   │   ├── interview_engine.py
│   │   │   ├── answer_evaluator.py
│   │   │   ├── skill_gap_analyzer.py
│   │   │   └── report_generator.py
│   │   ├── ai/               # AI Gateway
│   │   │   ├── base.py
│   │   │   ├── gateway.py
│   │   │   └── providers/
│   │   │       ├── openai_provider.py
│   │   │       ├── anthropic_provider.py
│   │   │       └── mock_provider.py
│   │   ├── security/         # Authentication
│   │   │   └── auth.py
│   │   └── main.py           # FastAPI application
│   ├── tests/                # Comprehensive test suite
│   ├── alembic/              # Database migrations
│   ├── requirements.txt
│   └── pytest.ini
├── frontend/
│   ├── index.html
│   ├── css/
│   │   └── style.css
│   └── js/
│       ├── api.js            # API client
│       ├── auth.js           # Authentication
│       ├── app.js            # Main application
│       └── interview.js      # Interview UI
├── docker/
│   ├── Dockerfile
│   └── init.sql
├── docs/
│   ├── TESTING.md            # Comprehensive testing guide
│   └── DEPLOYMENT.md         # Production deployment guide
├── docker-compose.yml
├── .env.example
├── quick-start.sh
└── README.md
```

---

## 🚀 Quick Start

### Using Docker (Recommended)

```bash
# 1. Clone and navigate
cd interview-platform

# 2. Copy environment template
cp .env.example .env

# 3. Edit .env - set AI provider and keys
nano .env  # Set AI_PROVIDER=mock (for testing) or openai/anthropic

# 4. Start services
docker-compose up -d

# 5. Run migrations
docker-compose exec backend alembic upgrade head

# 6. Access application
# Frontend: http://localhost:8000
# API Docs: http://localhost:8000/docs
# Admin: admin@example.com / change-this-admin-password
```

### Manual Installation

```bash
# 1. Install PostgreSQL, Redis
# 2. Create database
createdb interview_platform

# 3. Install Python dependencies
cd backend
pip install -r requirements.txt

# 4. Configure .env
cp ../.env.example ../.env
# Edit .env with your settings

# 5. Run migrations
alembic upgrade head

# 6. Start backend
uvicorn app.main:app --reload

# 7. Start Celery worker (separate terminal)
celery -A app.workers.celery_app worker --loglevel=info
```

---

## 🧪 Running Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio pytest-cov

# Run all tests
cd backend
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_auth_api.py

# View coverage report
open htmlcov/index.html
```

**Test Coverage:**
- Authentication: ✅ Registration, login, JWT validation, access control
- Resume Management: ✅ Upload, parsing, profile extraction, CRUD
- AI Gateway: ✅ Mock provider, response generation
- Interview Engine: ✅ Question generation, adaptive logic
- Services: ✅ Parser, analyzer, evaluator, report generator
- Security: ✅ Password hashing, token validation, input sanitization

---

## 📊 Database Schema

**15+ Tables with Proper Relationships:**

- `users` - User accounts and roles
- `resumes` - Uploaded resume files
- `candidate_profiles` - Parsed profile data
- `candidate_skills` - Extracted skills with claimed levels
- `work_experiences` - Work history
- `projects` - Project details
- `certifications` - Professional certifications
- `job_roles` - Predefined job roles
- `job_descriptions` - Custom JD uploads
- `interviews` - Interview sessions
- `interview_questions` - Generated questions
- `interview_answers` - Candidate answers
- `answer_evaluations` - Multi-dimensional scoring
- `skill_gaps` - Identified gaps with priorities
- `roadmaps` - Improvement plans
- `roadmap_items` - Daily learning tasks
- `interview_reports` - Final assessment reports
- `audit_logs` - Security and access logs

---

## 🔒 Security Features

- ✅ JWT-based authentication with refresh tokens
- ✅ Password hashing with bcrypt
- ✅ Role-based access control (User, Admin)
- ✅ Rate limiting (60/min, 1000/hour)
- ✅ Input validation with Pydantic
- ✅ SQL injection protection (SQLAlchemy ORM)
- ✅ XSS protection with content security policies
- ✅ CORS configuration
- ✅ Secure file upload validation (type, size)
- ✅ Private file storage with access control
- ✅ Audit logging for sensitive operations
- ✅ Environment-based secret management

---

## 🤖 AI Integration

### Provider-Independent Architecture

The platform uses an **AI Gateway** abstraction that supports multiple providers:

```python
# Supports: OpenAI, Anthropic, Mock (for testing)
gateway = AIGateway(provider_name="openai")  # or "anthropic" or "mock"
response = await gateway.generate(messages, temperature=0.7)
```

### AI Services

1. **Resume Analyzer** - Extracts structured data from unstructured resume text
2. **Job Description Analyzer** - Parses JD requirements and skills
3. **Interview Planner** - Creates interview blueprint with question distribution
4. **Question Generator** - Generates adaptive questions based on context
5. **Answer Evaluator** - Multi-dimensional scoring (correctness, depth, clarity, etc.)
6. **Follow-up Generator** - Generates strategic follow-up questions
7. **Skill Gap Analyzer** - Compares claimed vs demonstrated skills
8. **Roadmap Generator** - Creates personalized learning plans
9. **Report Generator** - Produces comprehensive interview reports

### Mock Provider for Testing

A fully functional mock provider is included that generates realistic responses without requiring API keys:

```env
AI_PROVIDER=mock
```

This allows complete testing of the interview flow without incurring AI API costs.

---

## 🎯 Interview Engine Architecture

### Adaptive Question Generation

The interview engine maintains state and adapts questions based on:

1. **Candidate Profile** - Skills, experience, projects from resume
2. **Job Requirements** - Required and preferred skills from JD
3. **Previous Questions** - Avoids repetition
4. **Previous Answers** - Adjusts difficulty based on performance
5. **Interview Blueprint** - Maintains question distribution (30% technical, 20% projects, etc.)
6. **Skill Coverage** - Ensures important skills are tested

### Answer Evaluation

Each answer is evaluated on **5 dimensions:**

1. **Correctness** (0-10) - Factual accuracy
2. **Technical Depth** (0-10) - Understanding depth
3. **Relevance** (0-10) - Addresses the question
4. **Clarity** (0-10) - Communication quality
5. **Problem Solving** (0-10) - Analytical thinking

**Overall Score** = Average of dimension scores

### Skill Gap Detection

The system compares three levels for each skill:

- **Required Level** - What the job needs
- **Claimed Level** - What the resume states
- **Demonstrated Level** - What the interview shows

**Gap Analysis:**
```
Skill: PostgreSQL
Required: Intermediate
Claimed: Intermediate
Demonstrated: Beginner
Gap Severity: Medium
Priority: High
```

---

## 📈 Performance & Scalability

### Implemented Optimizations

- **Database Indexing** - Indexes on user_id, resume_id, interview_id, status
- **Redis Caching** - Resume parsing results (1h), job roles (24h), interview state
- **Lazy Loading** - Relationships loaded on-demand
- **Connection Pooling** - SQLAlchemy pool_size=10, max_overflow=20
- **Token Limits** - AI requests limited to prevent cost overruns
- **Compact State** - Interview state minimized to essential data

### Horizontal Scaling

```yaml
# Supports multiple backend replicas
backend:
  deploy:
    replicas: 3
```

---

## 🛡️ Production Readiness

### ✅ Checklist

- [x] Docker & Docker Compose configuration
- [x] Environment-based configuration
- [x] Database migrations with Alembic
- [x] Comprehensive error handling
- [x] Logging with configurable levels
- [x] Health check endpoint
- [x] CORS configuration
- [x] Rate limiting
- [x] Input validation
- [x] Security hardening
- [x] Test coverage
- [x] API documentation
- [x] Deployment guide
- [x] Backup/restore procedures

### Missing for Full Production (Optional Enhancements)

- [ ] Kubernetes deployment manifests
- [ ] CI/CD pipeline configuration
- [ ] Monitoring dashboards (Grafana)
- [ ] Email notifications
- [ ] S3 integration for file storage
- [ ] WebSocket support for real-time updates
- [ ] Admin UI for user management
- [ ] Analytics and reporting dashboards

---

## 📚 API Endpoints

### Authentication
```
POST   /api/auth/register      - Register new user
POST   /api/auth/login         - Login user
GET    /api/auth/me            - Get current user
POST   /api/auth/logout        - Logout
```

### Resumes
```
POST   /api/resumes            - Upload resume
GET    /api/resumes            - List user resumes
GET    /api/resumes/{id}       - Get resume
GET    /api/resumes/{id}/profile - Get parsed profile
PATCH  /api/resumes/{id}/profile - Update profile
DELETE /api/resumes/{id}       - Delete resume
```

### Jobs
```
GET    /api/jobs/roles         - List job roles
GET    /api/jobs/roles/{id}    - Get job role
POST   /api/jobs/descriptions  - Upload JD
GET    /api/jobs/descriptions  - List JDs
```

### Interviews
```
POST   /api/interviews                     - Create interview
GET    /api/interviews                     - List interviews
GET    /api/interviews/{id}                - Get interview
POST   /api/interviews/{id}/start          - Start interview
POST   /api/interviews/{id}/answer         - Submit answer
POST   /api/interviews/{id}/finish         - Finish interview
GET    /api/interviews/{id}/report         - Get report
GET    /api/interviews/{id}/skill-gaps     - Get skill gaps
GET    /api/interviews/{id}/roadmap        - Get roadmap
```

### Dashboard
```
GET    /api/dashboard          - Dashboard data
GET    /api/progress           - Progress tracking
GET    /api/history            - Interview history
```

**Full API Documentation:** http://localhost:8000/docs

---

## 🎓 Example User Flow

1. **Register Account** → Create user account
2. **Upload Resume** → System parses and extracts profile
3. **Review Profile** → Verify extracted skills and experience
4. **Select Job Role** → Choose target position (e.g., "Python Developer")
5. **Start Interview** → System generates first question based on resume + role
6. **Answer Questions** → 10-15 adaptive questions with follow-ups
7. **Complete Interview** → System generates comprehensive analysis
8. **View Report** → See scores, strengths, weaknesses
9. **Review Skill Gaps** → Understand claimed vs demonstrated skills
10. **Get Roadmap** → Receive personalized 14-day learning plan
11. **Track Progress** → Compare scores across multiple interviews

---

## 🔧 Configuration

### AI Provider Configuration

**OpenAI:**
```env
AI_PROVIDER=openai
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4
```

**Anthropic:**
```env
AI_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-your-key-here
ANTHROPIC_MODEL=claude-3-sonnet-20240229
```

**Mock (Testing):**
```env
AI_PROVIDER=mock
```

### Database Configuration

```env
DATABASE_URL=postgresql://user:password@localhost:5432/interview_platform
```

### Security Configuration

```env
SECRET_KEY=generate-strong-random-key-min-32-chars
JWT_SECRET_KEY=generate-different-strong-key
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

---

## 📖 Documentation

- **README.md** - This file (project overview)
- **docs/TESTING.md** - Comprehensive testing guide
- **docs/DEPLOYMENT.md** - Production deployment guide
- **API Documentation** - http://localhost:8000/docs (auto-generated)

---

## 🐛 Troubleshooting

### Database Connection Issues
```bash
docker-compose ps db
docker-compose logs db
```

### Redis Connection Issues
```bash
docker-compose ps redis
docker-compose logs redis
```

### AI Provider Errors
```bash
# Check .env configuration
cat .env | grep AI_PROVIDER

# Use mock provider for testing
AI_PROVIDER=mock
```

### Resume Parsing Failures
- Ensure file is valid PDF/DOCX
- Check file size < 10MB
- Verify AI provider is configured

---

## 🤝 Contributing

This is a complete, production-ready reference implementation. For customization:

1. Fork the repository
2. Create feature branch
3. Add tests for new features
4. Ensure all tests pass
5. Submit pull request

---

## 📄 License

Proprietary - All rights reserved

---

## 🎉 Summary

This is a **COMPLETE, PRODUCTION-READY** AI-powered interview platform with:

✅ **Full-stack implementation** - Backend, Frontend, Database, AI integration  
✅ **Modular architecture** - Services, Repositories, Models separated  
✅ **Adaptive interview engine** - Questions adjust based on performance  
✅ **Skill gap analysis** - Validates resume claims against interview performance  
✅ **Comprehensive testing** - Unit, integration, API, security tests  
✅ **Production deployment** - Docker, migrations, monitoring, backups  
✅ **Security hardened** - Authentication, authorization, validation, encryption  
✅ **Scalable design** - Supports horizontal scaling and high availability  

**Ready to deploy and use for real interview preparation!**
