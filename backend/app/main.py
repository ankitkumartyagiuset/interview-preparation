from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import os
from app.core.config import settings
from app.core.database import init_db
from app.core.redis import init_redis
from app.api import auth, resumes, jobs, interviews, reports, dashboard


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    print("Starting application...")

    # Initialize database
    try:
        init_db()
        print("Database initialized")
    except Exception as e:
        print(f"Database initialization failed: {e}")

    # Initialize Redis
    try:
        init_redis()
        print("Redis initialized")
    except Exception as e:
        print(f"Redis initialization warning: {e}")

    # Create storage directories
    os.makedirs(settings.STORAGE_PATH, exist_ok=True)

    # Seed initial data
    from app.core.database import SessionLocal
    from app.models import JobRole, User, UserRole
    from app.security.auth import get_password_hash

    db = SessionLocal()
    try:
        # Create admin user if not exists
        admin = db.query(User).filter(User.email == settings.ADMIN_EMAIL).first()
        if not admin:
            admin = User(
                email=settings.ADMIN_EMAIL,
                hashed_password=get_password_hash(settings.ADMIN_PASSWORD),
                full_name="Admin User",
                role=UserRole.ADMIN,
                is_active=True
            )
            db.add(admin)
            print(f"Admin user created: {settings.ADMIN_EMAIL}")

        # Create sample job roles if not exist
        if db.query(JobRole).count() == 0:
            job_roles = [
                JobRole(
                    title="Python Developer",
                    description="Backend developer specializing in Python",
                    required_skills=["Python", "Django/Flask", "PostgreSQL", "REST APIs"],
                    preferred_skills=["Docker", "AWS", "Redis"],
                    responsibilities=["Develop backend services", "Write clean code", "Code reviews"],
                    experience_level="3-5 years"
                ),
                JobRole(
                    title="Full Stack Developer",
                    description="Full stack web development",
                    required_skills=["JavaScript", "React", "Node.js", "PostgreSQL"],
                    preferred_skills=["TypeScript", "Docker", "CI/CD"],
                    responsibilities=["Build web applications", "Frontend and backend development"],
                    experience_level="3-5 years"
                ),
                JobRole(
                    title="Frontend Developer",
                    description="Frontend web developer",
                    required_skills=["JavaScript", "React", "HTML/CSS", "REST APIs"],
                    preferred_skills=["TypeScript", "Next.js", "Tailwind CSS"],
                    responsibilities=["Build user interfaces", "Responsive design"],
                    experience_level="2-4 years"
                ),
                JobRole(
                    title="DevOps Engineer",
                    description="DevOps and infrastructure",
                    required_skills=["Docker", "Kubernetes", "AWS/Azure", "CI/CD", "Linux"],
                    preferred_skills=["Terraform", "Ansible", "Monitoring"],
                    responsibilities=["Manage infrastructure", "Deploy applications", "Monitor systems"],
                    experience_level="3-6 years"
                ),
                JobRole(
                    title="Data Engineer",
                    description="Data pipeline and warehousing",
                    required_skills=["Python", "SQL", "ETL", "Data Warehousing"],
                    preferred_skills=["Spark", "Airflow", "AWS", "Kafka"],
                    responsibilities=["Build data pipelines", "Data modeling"],
                    experience_level="3-5 years"
                )
            ]
            db.add_all(job_roles)
            print("Sample job roles created")

        db.commit()
    except Exception as e:
        print(f"Seeding error: {e}")
        db.rollback()
    finally:
        db.close()

    yield

    # Shutdown
    print("Shutting down application...")


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(auth.router, prefix=settings.API_PREFIX)
app.include_router(resumes.router, prefix=settings.API_PREFIX)
app.include_router(jobs.router, prefix=settings.API_PREFIX)
app.include_router(interviews.router, prefix=settings.API_PREFIX)
app.include_router(reports.router, prefix=settings.API_PREFIX)
app.include_router(dashboard.router, prefix=settings.API_PREFIX)

# Mount static files for frontend
frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend")
if os.path.exists(frontend_path):
    app.mount("/static", StaticFiles(directory=frontend_path), name="static")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "version": settings.APP_VERSION}


@app.get("/")
async def root():
    """Serve frontend"""
    frontend_index = os.path.join(os.path.dirname(__file__), "..", "frontend", "index.html")
    if os.path.exists(frontend_index):
        return FileResponse(frontend_index)
    return {"message": f"Welcome to {settings.APP_NAME} API", "docs": "/docs"}


@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    """Handle 404 errors - serve frontend for SPA routing"""
    if request.url.path.startswith("/api"):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": "Not found"}
        )

    frontend_index = os.path.join(os.path.dirname(__file__), "..", "frontend", "index.html")
    if os.path.exists(frontend_index):
        return FileResponse(frontend_index)

    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": "Not found"}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
