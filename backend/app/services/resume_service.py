import os
import uuid
import hashlib
from typing import Optional, Dict, Any, List
from fastapi import UploadFile, HTTPException, status
from sqlalchemy.orm import Session
from app.core.config import settings
from app.repositories.resume_repo import ResumeRepository
from app.repositories.audit_repo import AuditRepository
from app.ai.engines.resume_parser import resume_parser_engine
from app.models.resume import Resume, CandidateProfile

class ResumeService:
    def __init__(self, db: Session):
        self.db = db
        self.resume_repo = ResumeRepository(db)
        self.audit_repo = AuditRepository(db)

    async def upload_and_process_resume(self, user_id: int, file: UploadFile, provider_name: Optional[str] = None) -> Dict[str, Any]:
        # 1. Validate File extension
        ext = os.path.splitext(file.filename)[1].lower()
        if ext not in settings.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported file format: {ext}. Allowed formats: {settings.ALLOWED_EXTENSIONS}"
            )

        # 2. Read contents and check size
        contents = await file.read()
        if len(contents) > settings.MAX_UPLOAD_SIZE_BYTES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File exceeds maximum allowed size of {settings.MAX_UPLOAD_SIZE_BYTES // (1024*1024)}MB."
            )

        if len(contents) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Uploaded file is empty."
            )

        # Compute SHA-256 hash
        file_hash = hashlib.sha256(contents).hexdigest()

        # 3. Save to private storage
        storage_dir = os.path.join(settings.STORAGE_LOCAL_DIR, "resumes")
        os.makedirs(storage_dir, exist_ok=True)
        unique_filename = f"{uuid.uuid4().hex}_{file.filename}"
        file_path = os.path.join(storage_dir, unique_filename)

        with open(file_path, "wb") as f:
            f.write(contents)

        # 4. Create database record
        resume = self.resume_repo.create_resume(
            user_id=user_id,
            file_name=file.filename,
            file_path=file_path,
            file_size=len(contents),
            file_hash=file_hash,
            raw_text=""
        )

        try:
            # 5. Extract plain text
            raw_text = resume_parser_engine.extract_text_from_file(file_path)
            self.resume_repo.update_resume_status(resume, status="parsing", raw_text=raw_text)

            # 6. Structured AI extraction
            profile_data = await resume_parser_engine.extract_structured_profile(raw_text, provider_name=provider_name)

            # 7. Save candidate profile
            profile = self.resume_repo.create_or_update_profile(resume, profile_data)
            self.resume_repo.update_resume_status(resume, status="parsed")

            self.audit_repo.log(
                user_id=user_id,
                action="RESUME_PARSED",
                resource_type="resume",
                resource_id=str(resume.id),
                details_json={"file_name": file.filename, "skills_count": len(profile.skills)}
            )

            return {
                "resume_id": resume.id,
                "file_name": resume.file_name,
                "status": "parsed",
                "message": "Resume uploaded and analyzed successfully.",
                "profile": profile
            }

        except Exception as e:
            self.resume_repo.update_resume_status(resume, status="failed")
            self.audit_repo.log(
                user_id=user_id,
                action="RESUME_PARSE_FAILED",
                resource_type="resume",
                resource_id=str(resume.id),
                details_json={"error": str(e)}
            )
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Failed to extract structured data from resume: {str(e)}"
            )

    def get_resume(self, resume_id: int, user_id: int) -> Resume:
        resume = self.resume_repo.get_by_id(resume_id, user_id=user_id)
        if not resume:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resume not found."
            )
        return resume

    def list_resumes(self, user_id: int) -> List[Resume]:
        return self.resume_repo.list_by_user(user_id)

    def update_profile(self, resume_id: int, user_id: int, update_data: Dict[str, Any]) -> CandidateProfile:
        resume = self.get_resume(resume_id, user_id)
        profile = self.resume_repo.create_or_update_profile(resume, update_data)
        self.audit_repo.log(
            user_id=user_id,
            action="PROFILE_UPDATED",
            resource_type="candidate_profile",
            resource_id=str(profile.id)
        )
        return profile

    def delete_resume(self, resume_id: int, user_id: int) -> bool:
        resume = self.get_resume(resume_id, user_id)
        self.resume_repo.soft_delete_resume(resume)
        
        # Cleanup file if local
        if os.path.exists(resume.file_path):
            try:
                os.remove(resume.file_path)
            except Exception:
                pass

        self.audit_repo.log(
            user_id=user_id,
            action="RESUME_DELETED",
            resource_type="resume",
            resource_id=str(resume_id)
        )
        return True
