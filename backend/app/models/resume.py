"""Compatibility exports for canonical resume models."""

from app.models import (
    CandidateProfile,
    CandidateSkill,
    Certification,
    Project,
    Resume,
    WorkExperience,
)

Experience = WorkExperience

__all__ = [
    "Resume",
    "CandidateProfile",
    "CandidateSkill",
    "Project",
    "Experience",
    "Certification",
]
