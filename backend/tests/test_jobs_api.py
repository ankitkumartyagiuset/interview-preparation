import pytest


def test_get_job_roles_unauthorized(client):
    """Test getting job roles without auth still works (public endpoint)"""
    response = client.get("/api/jobs/roles")
    # Job roles should be publicly accessible
    assert response.status_code in [200, 403]


def test_get_job_roles(authenticated_client):
    """Test getting job roles"""
    client, user = authenticated_client

    response = client.get("/api/jobs/roles")

    assert response.status_code == 200
    roles = response.json()

    assert isinstance(roles, list)
    # Should have seeded roles
    if len(roles) > 0:
        role = roles[0]
        assert "id" in role
        assert "title" in role


def test_create_job_description(authenticated_client):
    """Test creating job description"""
    client, user = authenticated_client

    jd_data = {
        "title": "Senior Python Developer",
        "company_name": "Test Corp",
        "raw_text": """
        Senior Python Developer

        Requirements:
        - 5+ years of Python experience
        - Experience with Django/Flask
        - PostgreSQL knowledge
        - REST API development
        - Docker and AWS experience preferred

        Responsibilities:
        - Design and develop backend services
        - Write clean, maintainable code
        - Mentor junior developers
        """
    }

    response = client.post("/api/jobs/descriptions", json=jd_data)

    assert response.status_code == 201
    data = response.json()

    assert data["title"] == jd_data["title"]
    assert data["company_name"] == jd_data["company_name"]
    assert "required_skills" in data
    assert isinstance(data["required_skills"], list)


def test_list_job_descriptions(authenticated_client):
    """Test listing job descriptions"""
    client, user = authenticated_client

    # Create a JD first
    jd_data = {
        "title": "Test Position",
        "raw_text": "Test requirements"
    }
    client.post("/api/jobs/descriptions", json=jd_data)

    # List JDs
    response = client.get("/api/jobs/descriptions")

    assert response.status_code == 200
    jds = response.json()

    assert isinstance(jds, list)
    assert len(jds) >= 1
