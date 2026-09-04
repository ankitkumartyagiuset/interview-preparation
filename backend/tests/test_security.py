import pytest
from app.security.auth import get_password_hash, verify_password, create_access_token, decode_token


def test_password_hashing():
    """Test password hashing and verification"""
    password = "testpassword123"
    hashed = get_password_hash(password)

    assert hashed != password
    assert verify_password(password, hashed)
    assert not verify_password("wrongpassword", hashed)


def test_jwt_token_creation_and_decoding():
    """Test JWT token creation and decoding"""
    data = {"sub": "123"}
    token = create_access_token(data)

    assert isinstance(token, str)
    assert len(token) > 0

    decoded = decode_token(token)
    assert decoded["sub"] == "123"
    assert "exp" in decoded


def test_invalid_token_decoding():
    """Test decoding invalid token"""
    with pytest.raises(Exception):
        decode_token("invalid_token")
