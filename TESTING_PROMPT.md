# AI Resume-Based Interview Platform - Comprehensive Testing Prompt

## TEST STRATEGY

This document provides a systematic testing approach to verify and fix the complete application. Tests are organized by layers and must be executed in order.

---

## PHASE 0: SETUP & PREREQUISITES

### Step 0.1: Verify Environment
```
Python 3.10+ installed
pip installed
workspace path: c:\Users\hp\Desktop\ai interview prep
```

### Step 0.2: Install Dependencies
```powershell
cd c:\Users\hp\Desktop\ai interview prep
pip install -r requirements.txt
```

**Expected Outcome:**
- All packages installed successfully
- No version conflicts
- No missing packages

**Fix if fails:**
- Update requirements.txt with correct versions
- Clear pip cache: `pip cache purge`
- Reinstall: `pip install -r requirements.txt --force-reinstall`

---

## PHASE 1: DATABASE & MODELS

### Test 1.1: Database Initialization
**Goal:** Verify SQLite database creates and tables are generated

```powershell
cd c:\Users\hp\Desktop\ai interview prep
python -c "
from backend.app.core.database import engine, Base
from backend.app.models.user import User
from backend.app.models.interview import Interview
from backend.app.models.job import JobRole, JobDescription
Base.metadata.create_all(bind=engine)
print('✓ Database initialized successfully')
"
```

**Expected Output:**
- File created: `talentpulse.db` in project root
- No errors
- Output: `✓ Database initialized successfully`

**Fix if fails:**
- Check if models are properly imported
- Verify SQLite PATH in config.py
- Check file permissions

---

### Test 1.2: Check All Models Exist
**Goal:** Verify all 15+ required models are defined

Required models:
- User ✓
- Resume
- CandidateProfile
- Skill, CandidateSkill
- Project
- Experience
- Certification
- JobRole ✓
- JobDescription
- Interview
- InterviewQuestion
- InterviewAnswer
- AnswerEvaluation
- SkillGap
- Roadmap, RoadmapItem
- Report
- AuditLog ✓

**Test Command:**
```powershell
cd c:\Users\hp\Desktop\ai interview prep
python -c "
from backend.app.models.user import User
from backend.app.models.interview import Interview
from backend.app.models.job import JobRole, JobDescription
print('✓ Core models imported')
"
```

**Fix if missing:**
- Create model files for: Resume, CandidateProfile, Skill, Project, Experience, Certification, InterviewQuestion, InterviewAnswer, AnswerEvaluation, SkillGap, Roadmap, Report
- Add proper relationships and constraints
- Reference existing models for patterns

---

## PHASE 2: API STARTUP & HEALTH

### Test 2.1: Backend Starts Successfully
**Goal:** Verify FastAPI app starts without errors

```powershell
cd c:\Users\hp\Desktop\ai interview prep
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```

**Expected Output:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete
```

**You should see:**
- Server starts on port 8000
- No import errors
- No database connection errors
- "Uvicorn running" message

**Fix if fails:**
- Import errors: Check syntax in main.py and routers
- Database errors: Check config.py DATABASE_URL
- Missing routers: Verify all imports in main.py exist

---

### Test 2.2: Health Check Endpoint
**Goal:** Verify API responds to requests

```powershell
# In another terminal
curl http://127.0.0.1:8000/docs
```

**Expected Outcome:**
- Swagger UI loads at http://127.0.0.1:8000/docs
- Shows all API endpoints
- Can see: `/api/v1/auth/*`, `/api/v1/resumes/*`, etc.

**Fix if fails:**
- Check if routers are included in main.py: `app.include_router()`
- Verify router prefixes match documentation
- Check CORS middleware configuration

---

## PHASE 3: AUTHENTICATION TESTING

### Test 3.1: User Registration
**Goal:** Test user registration with valid data

```powershell
curl -X POST "http://127.0.0.1:8000/api/v1/auth/register" `
  -H "Content-Type: application/json" `
  -d '{
    "email": "testuser@example.com",
    "password": "TestPassword@123",
    "full_name": "Test User",
    "role": "candidate"
  }'
```

**Expected Response (200 OK):**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "testuser@example.com",
    "full_name": "Test User",
    "role": "candidate"
  }
}
```

**Fix if fails:**
- Check AuthService.register() implementation
- Verify UserRepository.create() exists
- Check password hashing functions
- Verify JWT token creation

### Test 3.2: Duplicate Registration (Should Fail)
```powershell
curl -X POST "http://127.0.0.1:8000/api/v1/auth/register" `
  -H "Content-Type: application/json" `
  -d '{
    "email": "testuser@example.com",
    "password": "TestPassword@123",
    "full_name": "Test User",
    "role": "candidate"
  }'
```

**Expected Response (400 BAD REQUEST):**
```json
{"detail": "A user with this email address already exists."}
```

**Fix if fails:**
- Check email uniqueness constraint in User model
- Verify UserRepository.get_by_email()

---

### Test 3.3: User Login
**Goal:** Test authentication with valid credentials

```powershell
curl -X POST "http://127.0.0.1:8000/api/v1/auth/login" `
  -H "Content-Type: application/json" `
  -d '{
    "email": "testuser@example.com",
    "password": "TestPassword@123"
  }'
```

**Expected Response (200 OK):**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "user": {...}
}
```

**Fix if fails:**
- Check AuthService.login() implementation
- Verify password verification logic
- Check JWT generation

### Test 3.4: Login with Wrong Password (Should Fail)
```powershell
curl -X POST "http://127.0.0.1:8000/api/v1/auth/login" `
  -H "Content-Type: application/json" `
  -d '{
    "email": "testuser@example.com",
    "password": "WrongPassword"
  }'
```

**Expected Response (401 UNAUTHORIZED):**
```json
{"detail": "Incorrect email or password."}
```

**Fix if fails:**
- Check password verification: `verify_password()`
- Check error handling in AuthService.login()

---

## PHASE 4: RESUME MODULE

### Test 4.1: Resume Model Exists
**Goal:** Verify Resume model and relationships

```powershell
python -c "
from backend.app.models.resume import Resume
from backend.app.core.database import Base
print('✓ Resume model exists')
print('Columns:', [c.name for c in Resume.__table__.columns])
"
```

**Expected Columns:**
- id
- user_id (FK to users)
- file_path
- file_name
- extracted_text
- parsed_data_json
- status (pending, parsed, error)
- created_at, updated_at

**Fix if missing:**
- Create [backend/app/models/resume.py](backend/app/models/resume.py)

---

### Test 4.2: Resume Upload (Mock)
**Goal:** Test resume upload endpoint

```powershell
# Create a test PDF
echo "This is a test resume" > test_resume.txt

# Upload
curl -X POST "http://127.0.0.1:8000/api/v1/resumes/upload" `
  -H "Authorization: Bearer <ACCESS_TOKEN>" `
  -F "file=@test_resume.txt"
```

**Expected Response (200 OK):**
```json
{
  "id": 1,
  "file_name": "test_resume.txt",
  "status": "pending",
  "message": "Resume uploaded successfully"
}
```

**Fix if fails:**
- Create resumes router endpoint: POST /api/v1/resumes/upload
- Implement ResumeService.upload_resume()
- Verify file validation (size, extension)
- Check storage directory creation

---

### Test 4.3: Resume Parsing
**Goal:** Test AI parsing of resume

```powershell
curl -X POST "http://127.0.0.1:8000/api/v1/resumes/{resume_id}/parse" `
  -H "Authorization: Bearer <ACCESS_TOKEN>"
```

**Expected Response (200 OK):**
```json
{
  "id": 1,
  "status": "parsed",
  "extracted_profile": {
    "full_name": "...",
    "email": "...",
    "phone": "...",
    "summary": "...",
    "skills": [...],
    "experiences": [...],
    "education": [...],
    "projects": [...]
  }
}
```

**Fix if fails:**
- Implement ResumeParser AI engine
- Create parsing prompts
- Handle AI provider (mock or real)
- Store parsed data in database

---

## PHASE 5: JOB DESCRIPTION MODULE

### Test 5.1: Get Job Roles
**Goal:** Verify predefined job roles are available

```powershell
curl http://127.0.0.1:8000/api/v1/jobs/roles `
  -H "Authorization: Bearer <ACCESS_TOKEN>"
```

**Expected Response (200 OK):**
```json
{
  "roles": [
    {"id": 1, "title": "Python Developer", ...},
    {"id": 2, "title": "Java Developer", ...},
    ...
  ]
}
```

**Fix if fails:**
- Check if job_service.py seeds default roles
- Verify JobRole model has required fields
- Check startup event in main.py

---

### Test 5.2: Select Job Role
```powershell
curl -X POST "http://127.0.0.1:8000/api/v1/jobs/select-role" `
  -H "Authorization: Bearer <ACCESS_TOKEN>" `
  -H "Content-Type: application/json" `
  -d '{"role_id": 1}'
```

**Expected Response (200 OK):**
```json
{"message": "Role selected", "role": {...}}
```

---

## PHASE 6: INTERVIEW ENGINE

### Test 6.1: Create Interview
**Goal:** Test interview creation with resume + job role

```powershell
curl -X POST "http://127.0.0.1:8000/api/v1/interviews" `
  -H "Authorization: Bearer <ACCESS_TOKEN>" `
  -H "Content-Type: application/json" `
  -d '{
    "resume_id": 1,
    "job_role_id": 1,
    "interview_type": "technical",
    "difficulty": "intermediate"
  }'
```

**Expected Response (201 CREATED):**
```json
{
  "id": 1,
  "status": "created",
  "resume_id": 1,
  "job_role_id": 1,
  "interview_type": "technical",
  "difficulty": "intermediate",
  "blueprint": {
    "technical_weight": 40,
    "project_weight": 20,
    ...
  }
}
```

**Fix if fails:**
- Implement InterviewService.create_interview()
- Create interview blueprint generator
- Verify Interview model structure
- Check relationships to Resume and JobRole

---

### Test 6.2: Start Interview
```powershell
curl -X POST "http://127.0.0.1:8000/api/v1/interviews/{interview_id}/start" `
  -H "Authorization: Bearer <ACCESS_TOKEN>"
```

**Expected Response (200 OK):**
```json
{
  "interview_id": 1,
  "status": "in_progress",
  "current_question": {
    "id": 1,
    "question": "What is your experience with Python?",
    "question_type": "technical",
    "difficulty": "intermediate"
  }
}
```

**Fix if fails:**
- Implement first question generation
- Create InterviewQuestion model
- Implement QuestionGenerator AI engine

---

### Test 6.3: Submit Answer
```powershell
curl -X POST "http://127.0.0.1:8000/api/v1/interviews/{interview_id}/answer" `
  -H "Authorization: Bearer <ACCESS_TOKEN>" `
  -H "Content-Type: application/json" `
  -d '{
    "question_id": 1,
    "answer": "I have 5 years of Python experience..."
  }'
```

**Expected Response (200 OK):**
```json
{
  "answer_id": 1,
  "evaluation": {
    "score": 8,
    "correctness": 8,
    "relevance": 9,
    "depth": 7,
    "feedback": "Good answer with practical examples"
  },
  "next_question": {
    "id": 2,
    "question": "...",
    "difficulty": "intermediate"
  }
}
```

**Fix if fails:**
- Create InterviewAnswer model
- Implement AnswerEvaluator AI engine
- Create evaluation rubric
- Implement adaptive follow-up logic

---

### Test 6.4: No Duplicate Questions
**Goal:** Verify same question not asked twice

After submitting 5 answers:
```
Question 1 → Question 2 → Question 3 → Question 4 → Question 5
```

Verify:
- No duplicate question IDs
- Difficulty adapts based on performance
- All questions within interview blueprint categories

**Fix if fails:**
- Track asked question IDs in interview state
- Implement adaptive difficulty algorithm
- Check QuestionGenerator filter

---

### Test 6.5: Finish Interview
```powershell
curl -X POST "http://127.0.0.1:8000/api/v1/interviews/{interview_id}/finish" `
  -H "Authorization: Bearer <ACCESS_TOKEN>"
```

**Expected Response (200 OK):**
```json
{
  "interview_id": 1,
  "status": "completed",
  "overall_score": 76,
  "category_scores": {
    "technical": 82,
    "projects": 71,
    "problem_solving": 74,
    "communication": 68,
    "behavioral": 75
  }
}
```

**Fix if fails:**
- Calculate aggregate scores
- Update interview status to completed
- Trigger report generation

---

## PHASE 7: SKILL GAP ANALYSIS

### Test 7.1: Get Skill Gaps
```powershell
curl "http://127.0.0.1:8000/api/v1/interviews/{interview_id}/skill-gaps" `
  -H "Authorization: Bearer <ACCESS_TOKEN>"
```

**Expected Response (200 OK):**
```json
{
  "skill_gaps": [
    {
      "skill_name": "SQL",
      "required_level": "intermediate",
      "resume_claimed_level": "intermediate",
      "demonstrated_level": "beginner",
      "gap": "high",
      "priority": "high",
      "confidence": 0.85
    },
    {
      "skill_name": "Python",
      "required_level": "advanced",
      "resume_claimed_level": "advanced",
      "demonstrated_level": "intermediate",
      "gap": "medium",
      "priority": "high",
      "confidence": 0.90
    }
  ]
}
```

**Fix if fails:**
- Create SkillGap model
- Implement SkillGapEngine
- Ensure interviews capture demonstrated skills
- Compare claimed vs demonstrated levels

---

## PHASE 8: REPORT GENERATION

### Test 8.1: Generate Report
```powershell
curl "http://127.0.0.1:8000/api/v1/interviews/{interview_id}/report" `
  -H "Authorization: Bearer <ACCESS_TOKEN>"
```

**Expected Response (200 OK):**
```json
{
  "id": 1,
  "interview_id": 1,
  "candidate_name": "Test User",
  "target_role": "Python Developer",
  "overall_readiness": 76,
  "technical_score": 82,
  "project_score": 71,
  "problem_solving_score": 74,
  "communication_score": 68,
  "behavioral_score": 75,
  "strengths": [...],
  "weaknesses": [...],
  "skill_gaps": [...],
  "improvement_roadmap": [...],
  "next_steps": [...]
}
```

**Fix if fails:**
- Create Report model
- Implement ReportGenerator
- Aggregate all interview data
- Generate roadmap recommendations

---

## PHASE 9: DASHBOARD

### Test 9.1: Get Dashboard Data
```powershell
curl "http://127.0.0.1:8000/api/v1/dashboard" `
  -H "Authorization: Bearer <ACCESS_TOKEN>"
```

**Expected Response (200 OK):**
```json
{
  "user": {...},
  "overall_readiness": 76,
  "recent_interviews": [...],
  "skill_gaps": [...],
  "improvement_roadmap": {...},
  "progress_chart": [
    {"interview_num": 1, "score": 61},
    {"interview_num": 2, "score": 68},
    {"interview_num": 3, "score": 76}
  ]
}
```

**Fix if fails:**
- Implement DashboardService
- Calculate aggregate statistics
- Fetch interview history
- Sort and order data properly

---

## PHASE 10: SECURITY & PROTECTION

### Test 10.1: Protected Endpoints Require Auth
```powershell
# Without token - should be 401
curl "http://127.0.0.1:8000/api/v1/resumes"
# Expected: 401 Unauthorized

# With token - should work
curl "http://127.0.0.1:8000/api/v1/resumes" `
  -H "Authorization: Bearer <ACCESS_TOKEN>"
```

**Fix if fails:**
- Check `get_current_user_id_and_role` dependency
- Verify JWT decoding
- Add Depends() to all protected endpoints

---

### Test 10.2: RBAC - Admin Access Only
```powershell
# As candidate - should fail (403)
curl "http://127.0.0.1:8000/api/v1/admin/users" `
  -H "Authorization: Bearer <CANDIDATE_TOKEN>"

# As admin - should work (200)
curl "http://127.0.0.1:8000/api/v1/admin/users" `
  -H "Authorization: Bearer <ADMIN_TOKEN>"
```

**Fix if fails:**
- Implement `require_admin` dependency
- Check role in token
- Return 403 for non-admins

---

### Test 10.3: Input Validation
Test with malicious inputs:

```powershell
# SQL injection attempt
curl -X POST "http://127.0.0.1:8000/api/v1/auth/register" `
  -d '{
    "email": "'; DROP TABLE users; --",
    "password": "test",
    "full_name": "test"
  }'
# Should reject - 422 Unprocessable Entity

# XSS attempt
curl -X POST "http://127.0.0.1:8000/api/v1/auth/register" `
  -d '{
    "email": "test@test.com",
    "full_name": "<script>alert()</script>",
    "password": "test"
  }'
# Should reject or sanitize - 422
```

**Fix if fails:**
- Add Pydantic validators
- Sanitize HTML input
- Use parameterized queries (SQLAlchemy does this by default)

---

## PHASE 11: FRONTEND TESTING

### Test 11.1: Login Page Loads
```powershell
curl http://127.0.0.1:8000/login
```

**Expected Response:**
- HTML page loads
- Contains login form
- Has email, password fields

**Fix if fails:**
- Check templates path in main.py
- Verify login.html exists
- Check template mounting

---

### Test 11.2: Dashboard Page (After Login)
Navigate to `http://127.0.0.1:8000/dashboard`

**Should show:**
- User name
- Overall readiness percentage
- Recent interviews
- Skill gaps
- Improvement roadmap

**Fix if fails:**
- Implement dashboard.html template
- Connect to dashboard API endpoint
- Render data from API response

---

## PHASE 12: END-TO-END FLOW

### Complete User Journey:
1. ✓ Register new account
2. ✓ Login
3. ✓ Upload resume
4. ✓ Parse resume (automatic)
5. ✓ Select job role
6. ✓ Start interview
7. ✓ Answer 5+ questions
8. ✓ Verify adaptive follow-ups
9. ✓ Finish interview
10. ✓ View report
11. ✓ Check skill gaps
12. ✓ View improvement roadmap
13. ✓ Dashboard shows progress
14. ✓ Start second interview
15. ✓ Verify score improved
16. ✓ Logout

---

## PHASE 13: ERROR HANDLING

### Test Error Scenarios:
1. **Missing resume before interview** → 400 Bad Request
2. **Invalid job role ID** → 404 Not Found
3. **Interview already finished** → 409 Conflict
4. **File too large** → 413 Payload Too Large
5. **Unsupported file type** → 422 Unprocessable Entity
6. **Database connection down** → 503 Service Unavailable
7. **AI provider timeout** → 504 Gateway Timeout (with graceful fallback)

**Fix if fails:**
- Add proper exception handling in services
- Return meaningful error codes
- Log errors for debugging

---

## FINAL CHECKLIST

- [ ] Phase 0: Environment setup complete
- [ ] Phase 1: Database initialized & models work
- [ ] Phase 2: API starts & health check passes
- [ ] Phase 3: Auth register/login working
- [ ] Phase 4: Resume upload & parsing working
- [ ] Phase 5: Job roles available
- [ ] Phase 6: Interview engine creates, generates questions
- [ ] Phase 7: Skill gaps calculated correctly
- [ ] Phase 8: Reports generated
- [ ] Phase 9: Dashboard displays data
- [ ] Phase 10: Security & RBAC working
- [ ] Phase 11: Frontend pages render
- [ ] Phase 12: End-to-end flow completes
- [ ] Phase 13: Error handling graceful

---

## FIX PRIORITY

If tests fail, fix in this order:
1. **CRITICAL**: Database & Models
2. **CRITICAL**: API Startup & Auth
3. **HIGH**: Resume Module
4. **HIGH**: Interview Engine
5. **MEDIUM**: Skill Gaps & Reports
6. **MEDIUM**: Dashboard
7. **LOW**: Frontend UI Polish

---

## NOTES

- Keep track of each test result
- Document failures with exact error messages
- Fix one phase before moving to next
- Rerun failed tests after fixing
- Ensure no regression in previous phases
