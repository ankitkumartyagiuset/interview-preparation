import pytest
import os
import tempfile
from app.services.resume_parser import ResumeParser


def test_validate_file_valid():
    """Test file validation with valid file"""
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f:
        f.write(b'test content')
        f.flush()
        file_path = f.name

    try:
        is_valid, error = ResumeParser.validate_file(file_path, 1024)
        assert is_valid
        assert error is None
    finally:
        os.unlink(file_path)


def test_validate_file_too_large():
    """Test file validation with oversized file"""
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f:
        f.write(b'x' * (11 * 1024 * 1024))  # 11 MB
        f.flush()
        file_path = f.name

    try:
        is_valid, error = ResumeParser.validate_file(file_path, 11 * 1024 * 1024)
        assert not is_valid
        assert "exceeds" in error.lower()
    finally:
        os.unlink(file_path)


def test_validate_file_invalid_extension():
    """Test file validation with invalid extension"""
    with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as f:
        f.write(b'test content')
        f.flush()
        file_path = f.name

    try:
        is_valid, error = ResumeParser.validate_file(file_path, 1024)
        assert not is_valid
        assert "not allowed" in error.lower()
    finally:
        os.unlink(file_path)


def test_validate_file_not_exists():
    """Test file validation with non-existent file"""
    is_valid, error = ResumeParser.validate_file("/nonexistent/file.pdf", 1024)
    assert not is_valid
    assert "not exist" in error.lower()


@pytest.mark.asyncio
async def test_resume_analyzer():
    """Test resume analyzer"""
    from app.services.resume_analyzer import ResumeAnalyzer

    analyzer = ResumeAnalyzer()

    sample_resume = """
    John Doe
    john.doe@email.com
    +1-555-0123

    EXPERIENCE
    Senior Software Engineer at Tech Corp (2020-Present)
    - Developed microservices using Python and Django
    - Improved system performance by 40%

    Software Engineer at StartupXYZ (2018-2020)
    - Built REST APIs with Flask

    SKILLS
    Python, Django, Flask, PostgreSQL, Docker, AWS

    EDUCATION
    BS Computer Science, University of California, 2018
    """

    profile = await analyzer.extract_structured_profile(sample_resume)

    assert profile is not None
    assert isinstance(profile, dict)
    assert "skills" in profile or "full_name" in profile
