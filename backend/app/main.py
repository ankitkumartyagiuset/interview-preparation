import os
from fastapi import FastAPI, Depends, Request, Response, status, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from backend.app.core.config import settings
from backend.app.core.database import engine, Base, get_db
from backend.app.core.security import decode_token, get_token_from_request
from backend.app.models.job import JobRole
from backend.app.services.job_service import JobService
from backend.app.services.auth_service import AuthService
from backend.app.services.dashboard_service import DashboardService

# Import routers
from backend.app.api.v1.auth import router as auth_router
from backend.app.api.v1.resumes import router as resumes_router
from backend.app.api.v1.jobs import router as jobs_router
from backend.app.api.v1.interviews import router as interviews_router
from backend.app.api.v1.reports import router as reports_router
from backend.app.api.v1.dashboard import router as dashboard_router
from backend.app.api.v1.admin import router as admin_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    description="Conversational AI mock interviews and targeted skill gap analysis platforms."
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
frontend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../frontend"))
static_dir = os.path.join(frontend_dir, "static")
templates_dir = os.path.join(frontend_dir, "templates")

# Ensure static directories exist
os.makedirs(os.path.join(static_dir, "css"), exist_ok=True)
os.makedirs(os.path.join(static_dir, "js"), exist_ok=True)

app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Templates
templates = Jinja2Templates(directory=templates_dir)

# Initialize database tables and seed roles on startup
@app.on_event("startup")
def startup_event():
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    # Seed default Job Roles if table is empty
    db = next(get_db())
    try:
        if db.query(JobRole).count() == 0:
            default_roles = [
                {
                    "title": "Software Developer",
                    "department": "Engineering",
                    "seniority": "intermediate",
                    "description": "General Software Developer focused on building clean, modular application logic, writing automated tests, and working across backend/frontend frameworks.",
                    "core_skills_json": [
                        {"name": "Python", "level": "advanced", "importance": "required"},
                        {"name": "SQL", "level": "intermediate", "importance": "required"},
                        {"name": "Git", "level": "advanced", "importance": "required"},
                        {"name": "REST APIs", "level": "advanced", "importance": "required"}
                    ],
                    "default_blueprint_json": {
                        "technical_weight": 35,
                        "project_weight": 25,
                        "problem_solving_weight": 20,
                        "communication_weight": 10,
                        "behavioral_weight": 10,
                        "role_specific_weight": 0
                    }
                },
                {
                    "title": "Python Developer",
                    "department": "Engineering",
                    "seniority": "intermediate",
                    "description": "Python Software Engineer responsible for writing clean, optimized backend code, database integrations, and implementing FastAPI/Django backend applications.",
                    "core_skills_json": [
                        {"name": "Python", "level": "advanced", "importance": "required"},
                        {"name": "FastAPI", "level": "intermediate", "importance": "required"},
                        {"name": "PostgreSQL", "level": "intermediate", "importance": "required"},
                        {"name": "Docker", "level": "intermediate", "importance": "preferred"},
                        {"name": "Data Structures", "level": "advanced", "importance": "required"}
                    ],
                    "default_blueprint_json": {
                        "technical_weight": 40,
                        "project_weight": 20,
                        "problem_solving_weight": 20,
                        "communication_weight": 10,
                        "behavioral_weight": 10,
                        "role_specific_weight": 0
                    }
                },
                {
                    "title": "Java Developer",
                    "department": "Engineering",
                    "seniority": "intermediate",
                    "description": "Java Developer responsible for building scalable enterprise microservices using Spring Boot, JPA, Hibernate and relational databases.",
                    "core_skills_json": [
                        {"name": "Java", "level": "advanced", "importance": "required"},
                        {"name": "Spring Boot", "level": "advanced", "importance": "required"},
                        {"name": "MySQL", "level": "intermediate", "importance": "required"},
                        {"name": "Microservices", "level": "intermediate", "importance": "preferred"}
                    ],
                    "default_blueprint_json": {
                        "technical_weight": 35,
                        "project_weight": 25,
                        "problem_solving_weight": 20,
                        "communication_weight": 10,
                        "behavioral_weight": 10,
                        "role_specific_weight": 0
                    }
                },
                {
                    "title": "Web Developer",
                    "department": "Engineering",
                    "seniority": "intermediate",
                    "description": "Front-end and full-stack Web Developer focused on building clean, high-performance user interfaces using HTML, CSS, JavaScript, React, or modern frameworks.",
                    "core_skills_json": [
                        {"name": "JavaScript", "level": "advanced", "importance": "required"},
                        {"name": "HTML & CSS", "level": "advanced", "importance": "required"},
                        {"name": "React", "level": "intermediate", "importance": "required"},
                        {"name": "REST APIs", "level": "intermediate", "importance": "required"}
                    ],
                    "default_blueprint_json": {
                        "technical_weight": 30,
                        "project_weight": 30,
                        "problem_solving_weight": 20,
                        "communication_weight": 10,
                        "behavioral_weight": 10,
                        "role_specific_weight": 0
                    }
                },
                {
                    "title": "Data Analyst",
                    "department": "Analytics",
                    "seniority": "intermediate",
                    "description": "Data Analyst responsible for exploring datasets, translating business requests into SQL queries, building dashboards, and generating actionable business insights.",
                    "core_skills_json": [
                        {"name": "SQL", "level": "advanced", "importance": "required"},
                        {"name": "Python", "level": "intermediate", "importance": "preferred"},
                        {"name": "Excel", "level": "advanced", "importance": "required"},
                        {"name": "Data Visualization", "level": "advanced", "importance": "required"}
                    ],
                    "default_blueprint_json": {
                        "technical_weight": 30,
                        "project_weight": 20,
                        "problem_solving_weight": 30,
                        "communication_weight": 10,
                        "behavioral_weight": 10,
                        "role_specific_weight": 0
                    }
                },
                {
                    "title": "Data Scientist",
                    "department": "Data Science",
                    "seniority": "intermediate",
                    "description": "Data Scientist skilled in statistical modeling, machine learning, data engineering, and implementing predictive pipelines in production environments.",
                    "core_skills_json": [
                        {"name": "Python", "level": "advanced", "importance": "required"},
                        {"name": "SQL", "level": "intermediate", "importance": "required"},
                        {"name": "Machine Learning", "level": "advanced", "importance": "required"},
                        {"name": "Pandas & NumPy", "level": "advanced", "importance": "required"}
                    ],
                    "default_blueprint_json": {
                        "technical_weight": 35,
                        "project_weight": 25,
                        "problem_solving_weight": 20,
                        "communication_weight": 10,
                        "behavioral_weight": 10,
                        "role_specific_weight": 0
                    }
                },
                {
                    "title": "AI/ML Engineer",
                    "department": "AI Research",
                    "seniority": "intermediate",
                    "description": "AI/ML Engineer specializing in training neural networks, using deep learning frameworks, fine-tuning large language models (LLMs), and production deployment of AI models.",
                    "core_skills_json": [
                        {"name": "Python", "level": "advanced", "importance": "required"},
                        {"name": "PyTorch", "level": "intermediate", "importance": "required"},
                        {"name": "Deep Learning", "level": "advanced", "importance": "required"},
                        {"name": "LLMs & GenAI", "level": "intermediate", "importance": "preferred"}
                    ],
                    "default_blueprint_json": {
                        "technical_weight": 40,
                        "project_weight": 20,
                        "problem_solving_weight": 20,
                        "communication_weight": 10,
                        "behavioral_weight": 10,
                        "role_specific_weight": 0
                    }
                },
                {
                    "title": "Cloud Engineer",
                    "department": "DevOps / Infrastructure",
                    "seniority": "intermediate",
                    "description": "Cloud Infrastructure Engineer responsible for deploying AWS/Azure systems, configuring networks, CI/CD pipelines, and maintaining platform uptime.",
                    "core_skills_json": [
                        {"name": "AWS", "level": "advanced", "importance": "required"},
                        {"name": "Docker", "level": "advanced", "importance": "required"},
                        {"name": "Terraform", "level": "intermediate", "importance": "required"},
                        {"name": "CI/CD Pipelines", "level": "advanced", "importance": "required"}
                    ],
                    "default_blueprint_json": {
                        "technical_weight": 35,
                        "project_weight": 25,
                        "problem_solving_weight": 20,
                        "communication_weight": 10,
                        "behavioral_weight": 10,
                        "role_specific_weight": 0
                    }
                }
            ]
            for r in default_roles:
                job_role = JobRole(
                    title=r["title"],
                    department=r["department"],
                    seniority=r["seniority"],
                    description=r["description"],
                    core_skills_json=r["core_skills_json"],
                    default_blueprint_json=r["default_blueprint_json"]
                )
                db.add(job_role)
            db.commit()
    finally:
        db.close()

# Include API Routers
app.include_router(auth_router, prefix=settings.API_V1_STR)
app.include_router(resumes_router, prefix=settings.API_V1_STR)
app.include_router(jobs_router, prefix=settings.API_V1_STR)
app.include_router(interviews_router, prefix=settings.API_V1_STR)
app.include_router(reports_router, prefix=settings.API_V1_STR)
app.include_router(dashboard_router, prefix=settings.API_V1_STR)
app.include_router(admin_router, prefix=settings.API_V1_STR)

# --- Template Helpers ---
def get_user_from_cookie(request: Request) -> Optional[dict]:
    token = request.cookies.get("access_token")
    if token:
        if token.startswith("Bearer "):
            token = token[7:]
        payload = decode_token(token)
        if payload and payload.get("type") == "access":
            return {"user_id": int(payload.get("sub")), "role": payload.get("role", "candidate")}
    return None

# --- Web Page Routes ---
@app.get("/", response_class=HTMLResponse)
def home_page(request: Request):
    user = get_user_from_cookie(request)
    if user:
        return RedirectResponse(url="/dashboard")
    return templates.TemplateResponse(request=request, name="login.html")

@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    user = get_user_from_cookie(request)
    if user:
        return RedirectResponse(url="/dashboard")
    return templates.TemplateResponse(request=request, name="login.html")

@app.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    user = get_user_from_cookie(request)
    if user:
        return RedirectResponse(url="/dashboard")
    return templates.TemplateResponse(request=request, name="register.html")

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard_page(request: Request):
    user = get_user_from_cookie(request)
    if not user:
        return RedirectResponse(url="/login")
    return templates.TemplateResponse(request=request, name="dashboard.html")

@app.get("/upload", response_class=HTMLResponse)
def upload_page(request: Request):
    user = get_user_from_cookie(request)
    if not user:
        return RedirectResponse(url="/login")
    return templates.TemplateResponse(request=request, name="upload.html")

@app.get("/interview/{interview_id}", response_class=HTMLResponse)
def interview_page(interview_id: int, request: Request):
    user = get_user_from_cookie(request)
    if not user:
        return RedirectResponse(url="/login")
    return templates.TemplateResponse(request=request, name="interview.html", context={"interview_id": interview_id})

@app.get("/report/{interview_id}", response_class=HTMLResponse)
def report_page(interview_id: int, request: Request):
    user = get_user_from_cookie(request)
    if not user:
        return RedirectResponse(url="/login")
    return templates.TemplateResponse(request=request, name="report.html", context={"interview_id": interview_id})
