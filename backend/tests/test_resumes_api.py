import pytest
from io import BytesIO


def test_list_resumes_empty(authenticated_client):
    """Test listing resumes when none exist"""
    client, user = authenticated_client

    response = client.get("/api/resumes")

    assert response.status_code == 200
    resumes = response.json()

    assert isinstance(resumes, list)
    assert len(resumes) == 0


def test_upload_resume_invalid_type(authenticated_client):
    """Test uploading invalid file type"""
    client, user = authenticated_client

    # Create a text file
    file_content = b"This is a text file"
    files = {"file": ("test.txt", BytesIO(file_content), "text/plain")}

    response = client.post("/api/resumes", files=files)

    assert response.status_code == 400
    assert "not allowed" in response.json()["detail"].lower()


def test_get_resume_not_found(authenticated_client):
    """Test getting non-existent resume"""
    client, user = authenticated_client

    response = client.get("/api/resumes/99999")

    assert response.status_code == 404


def test_delete_resume_not_found(authenticated_client):
    """Test deleting non-existent resume"""
    client, user = authenticated_client

    response = client.delete("/api/resumes/99999")

    assert response.status_code == 404


def test_resumes_unauthorized(client):
    """Test accessing resumes without authentication"""
    response = client.get("/api/resumes")

    assert response.status_code == 403  # Unauthorized
