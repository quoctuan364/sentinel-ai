import os
import pytest
from app.scanners.ast_scanner import scan_python_ast
from app.scanners.fingerprint import generate_fingerprint
from app.scanners.runner import scan_directory
from app.scanners.sarif import export_to_sarif
from app.scanners.secrets import scan_file_for_secrets


def test_ast_scanner_vulnerabilities():
    code = """
import os
import subprocess
import pickle
import hashlib

def bad_func(user_input):
    os.system(user_input)
    subprocess.run("ls " + user_input, shell=True)
    pickle.loads(user_input)
    eval(user_input)
    hashlib.md5(b"secret")
    cursor.execute(f"SELECT * FROM users WHERE id = '{user_input}'")
"""
    findings = scan_python_ast("test.py", code)
    assert len(findings) >= 5

    cwes = [f["cwe_id"] for f in findings]
    assert "CWE-78" in cwes   # Command injection
    assert "CWE-95" in cwes   # Eval code execution
    assert "CWE-502" in cwes  # Pickle deserialization
    assert "CWE-328" in cwes  # MD5 weak hash
    assert "CWE-89" in cwes   # SQL injection


def test_secret_scanner():
    code = """
AWS_KEY = "AKIAIOSFODNN7EXAMPLE"
GITHUB_KEY = "ghp_1234567890abcdefghijklmnopqrstuvwxyzAB"
DB_URI = "postgres://root:password123@localhost:5432/db"
"""
    findings = scan_file_for_secrets("config.py", code)
    assert len(findings) >= 2
    rule_ids = [f["rule_id"] for f in findings]
    assert "SECRET-002" in rule_ids  # AWS Key
    assert "SECRET-003" in rule_ids  # GitHub Token


def test_deterministic_fingerprint():
    fp1 = generate_fingerprint("bandit", "B608", "src/db.py", "SELECT * FROM users", 10)
    fp2 = generate_fingerprint("bandit", "B608", "src/db.py", "SELECT * FROM users", 15)  # Line moved
    # Fingerprint should be stable even if line number shifted because it matches code pattern and file
    assert fp1 == fp2


def test_sarif_export():
    sample_findings = [
        {
            "fingerprint": "abc1234",
            "scanner_name": "bandit",
            "rule_id": "B608",
            "title": "SQL Injection",
            "message": "Raw string in SQL execute",
            "severity": "CRITICAL",
            "confidence": "HIGH",
            "cwe_id": "CWE-89",
            "file_path": "app/db.py",
            "start_line": 12,
            "end_line": 12,
            "code_snippet": "cursor.execute(query)",
            "remediation_guidance": "Use parameter binding",
        }
    ]
    sarif = export_to_sarif(sample_findings)
    assert sarif["version"] == "2.1.0"
    assert len(sarif["runs"]) == 1
    assert len(sarif["runs"][0]["results"]) == 1
    assert sarif["runs"][0]["results"][0]["ruleId"] == "B608"
    assert sarif["runs"][0]["results"][0]["level"] == "error"


def test_fixture_scan():
    fixture_dir = "./fixtures/vulnerable-repo"
    assert os.path.exists(fixture_dir)
    findings = scan_directory(fixture_dir)
    assert len(findings) > 0
    # Should identify both secrets and AST issues
    scanners = set(f["scanner_name"] for f in findings)
    assert "bandit" in scanners
    assert "detect-secrets" in scanners
