import os
import pytest
from app.scanners.runner import scan_directory


def test_safe_fixture_zero_findings():
    """
    Ensure that defensive coding practices (parameterized queries, list-based subprocess,
    json parsing, sha256 hashing, environment variables) yield zero false positives.
    """
    safe_dir = "./fixtures/safe-repo"
    assert os.path.exists(safe_dir), "Safe fixture directory must exist"

    findings = scan_directory(safe_dir)
    assert len(findings) == 0, f"Expected 0 findings on safe fixture, but found {len(findings)}: {findings}"
