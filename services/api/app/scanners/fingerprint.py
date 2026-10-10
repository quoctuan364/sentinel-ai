import hashlib
import re


def generate_fingerprint(
    scanner_name: str,
    rule_id: str,
    file_path: str,
    code_snippet: str = "",
    start_line: int = 1
) -> str:
    """
    Generate a stable, deterministic cryptographic fingerprint for a finding.
    Normalizes whitespace and relative paths so findings remain stable across line shifts.
    """
    normalized_path = file_path.replace("\\", "/").strip().lstrip("./")
    # Normalize snippet: remove variable leading/trailing whitespace
    normalized_snippet = re.sub(r'\s+', ' ', (code_snippet or "").strip())
    
    # Hash combining scanner, rule, file path, and snippet context
    raw_payload = f"{scanner_name}:{rule_id}:{normalized_path}:{normalized_snippet}"
    return hashlib.sha256(raw_payload.encode("utf-8")).hexdigest()
