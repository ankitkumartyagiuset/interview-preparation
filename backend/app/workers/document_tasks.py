from celery.utils.log import get_task_logger

from app.workers.celery_app import celery_app


logger = get_task_logger(__name__)


@celery_app.task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=300,
    retry_kwargs={"max_retries": 3},
)
def process_resume(self, resume_id: int, user_id: int) -> dict:
    """Process a stored resume in a worker process.

    The task is intentionally keyed by IDs so it can be retried safely without
    serializing request objects or uploaded file contents through Redis.
    """
    from app.core.database import SessionLocal
    from app.services.resume_service import ResumeService

    db = SessionLocal()
    try:
        resume = ResumeService(db).get_resume(resume_id, user_id)
        logger.info("Resume %s is ready for asynchronous processing", resume.id)
        return {"resume_id": resume.id, "status": "queued"}
    finally:
        db.close()
