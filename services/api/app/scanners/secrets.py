import math
import re
from typing import Any, Dict, List
from app.scanners.fingerprint import generate_fingerprint


def calculate_shannon_entropy(data: str) -> float:
    """Calculate Shannon entropy to identify high-randomness secret strings."""
    if not data:
        return 0.0
    entropy = 0.0
    for x in set(data):
        p_x = float(data.count(x)) / len(data)
        if p_x > 0:
            entropy += - p_x * math.log2(p_x)
    return entropy


SECRET_PATTERNS = [
    {
        "rule_id": "SECRET-001",
        "title": "Private Key Detected",
        "severity": "CRITICAL",
        "confidence": "HIGH",
        "cwe_id": "CWE-798",
        "pattern": re.compile(r"-----BEGIN\s+(?:RSA|DSA|EC|OPENSSH|PGP)?\s*PRIVATE\s+KEY-----"),
        "remediation": "Revoke the private key immediately, remove it from git history using git-filter-repo, and store in a secure secret store (e.g. HashiCorp Vault or AWS Secrets Manager)."
    },
    {
        "rule_id": "SECRET-002",
        "title": "AWS Access Key ID Detected",
        "severity": "CRITICAL",
        "confidence": "HIGH",
        "cwe_id": "CWE-798",
        "pattern": re.compile(r"(?:A3T[A-Z0-9]|AKIA|AGPA|AIDA|AROA|AIPA|ANPA|ANVA|ASIA)[A-Z0-9]{16}"),
        "remediation": "Rotate AWS IAM access key immediately in AWS IAM console, check CloudTrail logs for unauthorized usage, and inject via AWS IAM Roles or environment variables."
    },
    {
        "rule_id": "SECRET-003",
        "title": "GitHub Token Detected",
        "severity": "CRITICAL",
        "confidence": "HIGH",
        "cwe_id": "CWE-798",
        "pattern": re.compile(r"(?:ghp|gho|ghu|ghs|ghr)_[a-zA-Z0-9]{36,255}"),
        "remediation": "Revoke the GitHub Personal Access Token or App installation token immediately in GitHub settings and configure GitHub Secrets for CI/CD."
    },
    {
        "rule_id": "SECRET-004",
        "title": "Slack Bot/Webhook Token Detected",
        "severity": "HIGH",
        "confidence": "HIGH",
        "cwe_id": "CWE-798",
        "pattern": re.compile(r"xox[baprs]-[0-9]{12}-[0-9]{12}-[a-zA-Z0-9]{24}"),
        "remediation": "Regenerate the Slack bot token in api.slack.com apps dashboard and migrate configuration to environment variables."
    },
    {
        "rule_id": "SECRET-005",
        "title": "Hardcoded Database Credentials in URI",
        "severity": "HIGH",
        "confidence": "HIGH",
        "cwe_id": "CWE-798",
        "pattern": re.compile(r"(?:postgres|mysql|mongodb|redis):\/\/[a-zA-Z0-9_\-\.]+:(?!(?:\$|%7B))[^@\s\t\r\n]{3,}@[a-zA-Z0-9_\-\.]+"),
        "remediation": "Do not commit raw connection strings with passwords. Reference credentials via environment variables (e.g., DATABASE_URL)."
    },
    {
        "rule_id": "SECRET-006",
        "title": "Hardcoded API Key / Secret Assignment",
        "severity": "MEDIUM",
        "confidence": "MEDIUM",
        "cwe_id": "CWE-798",
        "pattern": re.compile(r"(?i)(?:api_key|secret_key|auth_token|client_secret)\s*=\s*['\"][a-zA-Z0-9_\-\.]{16,}['\"]"),
        "remediation": "Extract hardcoded secret strings into environment variables or a key management service."
    }
]


def scan_file_for_secrets(file_path: str, content: str) -> List[Dict[str, Any]]:
    findings: List[Dict[str, Any]] = []
    lines = content.splitlines()

    for line_idx, line in enumerate(lines, start=1):
        # Ignore comments or mock documentation lines if specified
        stripped = line.strip()
        if stripped.startswith(("#", "//", "/*", "*")) and "example" in stripped.lower():
            continue

        for rule in SECRET_PATTERNS:
            match = rule["pattern"].search(line)
            if match:
                snippet = line.strip()
                # Redact the secret within the snippet before storage
                matched_str = match.group(0)
                if len(matched_str) > 8:
                    redacted_snippet = snippet.replace(matched_str, matched_str[:4] + "..." + matched_str[-4:])
                else:
                    redacted_snippet = snippet.replace(matched_str, "[REDACTED_SECRET]")

                fp = generate_fingerprint(
                    scanner_name="detect-secrets",
                    rule_id=rule["rule_id"],
                    file_path=file_path,
                    code_snippet=snippet,
                    start_line=line_idx
                )

                findings.append({
                    "fingerprint": fp,
                    "scanner_name": "detect-secrets",
                    "rule_id": rule["rule_id"],
                    "title": rule["title"],
                    "message": f"Found potential secret match ({rule['title']}) at line {line_idx}.",
                    "severity": rule["severity"],
                    "confidence": rule["confidence"],
                    "cwe_id": rule["cwe_id"],
                    "file_path": file_path,
                    "start_line": line_idx,
                    "end_line": line_idx,
                    "code_snippet": redacted_snippet,
                    "remediation_guidance": rule["remediation"],
                    "validation_status": "CONFIRMED",
                    "lifecycle_status": "OPEN",
                })
                break  # Stop checking rules for this line once matched

    return findings
