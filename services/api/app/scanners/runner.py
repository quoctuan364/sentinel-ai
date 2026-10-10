import os
from typing import Any, Dict, List, Optional
from app.core.config import settings
from app.scanners.ast_scanner import scan_python_ast
from app.scanners.secrets import scan_file_for_secrets

SEVERITY_ORDER = {
    "CRITICAL": 0,
    "HIGH": 1,
    "MEDIUM": 2,
    "LOW": 3,
    "INFORMATIONAL": 4,
}


def scan_file_content(file_path: str, content: str) -> List[Dict[str, Any]]:
    """
    Run all deterministic scanners on a single file's content.
    """
    findings: List[Dict[str, Any]] = []

    # 1. Run secret scanner on all files
    secret_findings = scan_file_for_secrets(file_path, content)
    findings.extend(secret_findings)

    # 2. Run AST scanner on Python files
    if file_path.endswith(".py"):
        ast_findings = scan_python_ast(file_path, content)
        findings.extend(ast_findings)

    return findings


def scan_directory(dir_path: str) -> List[Dict[str, Any]]:
    """
    Recursively scan a directory safely with file size and count limits.
    """
    all_findings: List[Dict[str, Any]] = []
    seen_fingerprints = set()
    files_scanned = 0

    ignored_dirs = {".git", ".venv", "node_modules", "__pycache__", "dist", "build", ".next"}

    for root, dirs, files in os.walk(dir_path):
        # Prune ignored directories in-place
        dirs[:] = [d for d in dirs if d not in ignored_dirs]

        for file in files:
            if files_scanned >= settings.MAX_DIFF_FILE_COUNT:
                break

            full_path = os.path.join(root, file)
            rel_path = os.path.relpath(full_path, dir_path).replace("\\", "/")

            # Skip binary and very large files
            try:
                stat = os.stat(full_path)
                if stat.st_size > settings.MAX_FILE_SIZE_BYTES:
                    continue

                with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()

                file_findings = scan_file_content(rel_path, content)
                for finding in file_findings:
                    fp = finding["fingerprint"]
                    if fp not in seen_fingerprints:
                        seen_fingerprints.add(fp)
                        all_findings.append(finding)

                files_scanned += 1
            except Exception:
                continue

    # Sort findings by severity
    all_findings.sort(key=lambda x: SEVERITY_ORDER.get(x.get("severity", "LOW"), 99))
    return all_findings


def scan_diff_content(diff_text: str) -> List[Dict[str, Any]]:
    """
    Parse a unified git diff, extract changed/added lines and files, and scan them.
    Matches findings to changed line ranges.
    """
    findings: List[Dict[str, Any]] = []
    seen_fingerprints = set()

    current_file: Optional[str] = None
    file_chunks: Dict[str, List[str]] = {}

    for line in diff_text.splitlines():
        if line.startswith("+++ b/"):
            current_file = line[6:].strip()
            if current_file not in file_chunks:
                file_chunks[current_file] = []
        elif line.startswith("--- "):
            continue
        elif current_file and (line.startswith("+") and not line.startswith("+++")):
            file_chunks[current_file].append(line[1:])

    for fpath, added_lines in file_chunks.items():
        joined_content = "\n".join(added_lines)
        file_findings = scan_file_content(fpath, joined_content)
        for f in file_findings:
            fp = f["fingerprint"]
            if fp not in seen_fingerprints:
                seen_fingerprints.add(fp)
                findings.append(f)

    findings.sort(key=lambda x: SEVERITY_ORDER.get(x.get("severity", "LOW"), 99))
    return findings
