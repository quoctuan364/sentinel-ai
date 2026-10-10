import hashlib
import hmac
import os
import re
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional, Union
import jwt
import bcrypt
from app.core.config import settings

ALGORITHM = "HS256"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
    except Exception:
        return False


def get_password_hash(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")



def create_access_token(
    subject: Union[str, Any],
    workspace_id: Optional[str] = None,
    role: Optional[str] = None,
    expires_delta: Optional[timedelta] = None
) -> str:
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode: Dict[str, Any] = {
        "exp": expire,
        "sub": str(subject),
        "iat": datetime.now(timezone.utc),
    }
    if workspace_id:
        to_encode["workspace_id"] = str(workspace_id)
    if role:
        to_encode["role"] = str(role)
        
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except (jwt.PyJWTError, Exception):
        return None


def verify_github_signature(payload_bytes: bytes, signature_header: Optional[str], secret: str) -> bool:
    """
    Verify GitHub webhook signature using constant-time comparison.
    Signature header format is: sha256=<hex_digest>
    """
    if not signature_header or not signature_header.startswith("sha256="):
        return False
    
    expected_hash = signature_header.split("sha256=", 1)[1].strip()
    mac = hmac.new(secret.encode("utf-8"), msg=payload_bytes, digestmod=hashlib.sha256)
    computed_hash = mac.hexdigest()
    
    return hmac.compare_digest(computed_hash, expected_hash)


def sanitize_log_message(message: str) -> str:
    """
    Redact secrets, tokens, and authorization credentials from logs.
    """
    # Redact GitHub tokens (ghp_, ghs_, gho_, github_pat_)
    message = re.sub(r'(gh[p|s|o]_[a-zA-Z0-9]{36,255})', '[REDACTED_GH_TOKEN]', message)
    message = re.sub(r'(github_pat_[a-zA-Z0-9_]{36,255})', '[REDACTED_PAT]', message)
    # Redact Bearer tokens
    message = re.sub(r'(Bearer\s+)[A-Za-z0-9\-_=.]+', r'\1[REDACTED_JWT]', message, flags=re.IGNORECASE)
    # Redact OpenAI keys
    message = re.sub(r'(sk-[a-zA-Z0-9]{20,})', '[REDACTED_OPENAI_KEY]', message)
    return message


def validate_path_safety(base_dir: str, target_path: str) -> bool:
    """
    Prevent path traversal and directory escapes.
    """
    base_resolved = os.path.abspath(base_dir)
    target_resolved = os.path.abspath(os.path.join(base_dir, target_path))
    return target_resolved.startswith(base_resolved)
