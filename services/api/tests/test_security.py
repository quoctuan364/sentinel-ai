import hashlib
import hmac
import pytest
from app.core.security import (
    create_access_token,
    decode_access_token,
    get_password_hash,
    sanitize_log_message,
    validate_path_safety,
    verify_github_signature,
    verify_password,
)


def test_password_hashing():
    pw = "SuperSecretPassword123!"
    hashed = get_password_hash(pw)
    assert hashed != pw
    assert verify_password(pw, hashed) is True
    assert verify_password("WrongPassword", hashed) is False


def test_jwt_token_flow():
    token = create_access_token(subject="user-123", workspace_id="ws-456", role="ADMIN")
    payload = decode_access_token(token)
    assert payload is not None
    assert payload["sub"] == "user-123"
    assert payload["workspace_id"] == "ws-456"
    assert payload["role"] == "ADMIN"


def test_jwt_invalid_token():
    payload = decode_access_token("invalid.token.signature")
    assert payload is None


def test_github_webhook_signature_verification():
    secret = "my-test-secret"
    body = b'{"action":"opened","pull_request":{"id":123}}'
    
    # Valid signature
    mac = hmac.new(secret.encode("utf-8"), msg=body, digestmod=hashlib.sha256)
    valid_sig = f"sha256={mac.hexdigest()}"
    assert verify_github_signature(body, valid_sig, secret) is True

    # Tampered body
    tampered_body = b'{"action":"closed"}'
    assert verify_github_signature(tampered_body, valid_sig, secret) is False

    # Invalid secret
    assert verify_github_signature(body, valid_sig, "wrong-secret") is False

    # Malformed header
    assert verify_github_signature(body, "malformed_signature", secret) is False
    assert verify_github_signature(body, None, secret) is False


def test_sanitize_log_secrets():
    raw_log = "Error connecting with token ghp_1234567890abcdefghijklmnopqrstuvwxyzAB and Bearer eyJhbGciOi..."
    sanitized = sanitize_log_message(raw_log)
    assert "ghp_" not in sanitized
    assert "[REDACTED_GH_TOKEN]" in sanitized
    assert "[REDACTED_JWT]" in sanitized


def test_path_traversal_prevention():
    base = "/var/app/repos"
    assert validate_path_safety(base, "repo1/app.py") is True
    assert validate_path_safety(base, "../../etc/passwd") is False
