import ast
from typing import Any, Dict, List
from app.scanners.fingerprint import generate_fingerprint


class SecurityASTVisitor(ast.NodeVisitor):
    def __init__(self, file_path: str, source_lines: List[str]):
        self.file_path = file_path
        self.source_lines = source_lines
        self.findings: List[Dict[str, Any]] = []

    def _get_line_snippet(self, lineno: int) -> str:
        if 1 <= lineno <= len(self.source_lines):
            return self.source_lines[lineno - 1].strip()
        return ""

    def visit_Call(self, node: ast.Call):
        # 1. Check for Command Injection: os.system, os.popen
        func_name = ""
        if isinstance(node.func, ast.Attribute):
            if isinstance(node.func.value, ast.Name):
                func_name = f"{node.func.value.id}.{node.func.attr}"
            else:
                func_name = node.func.attr
        elif isinstance(node.func, ast.Name):
            func_name = node.func.id

        # os.system or os.popen
        if func_name in ("os.system", "os.popen"):
            snippet = self._get_line_snippet(node.lineno)
            self.findings.append({
                "fingerprint": generate_fingerprint("bandit", "B605", self.file_path, snippet, node.lineno),
                "scanner_name": "bandit",
                "rule_id": "B605",
                "title": "Command Injection via os.system / os.popen",
                "message": f"Starting a process with a shell using '{func_name}' is susceptible to shell injection.",
                "severity": "CRITICAL",
                "confidence": "HIGH",
                "cwe_id": "CWE-78",
                "file_path": self.file_path,
                "start_line": node.lineno,
                "end_line": getattr(node, "end_lineno", node.lineno),
                "code_snippet": snippet,
                "remediation_guidance": "Use subprocess.run with arguments passed as a list, without shell=True.",
                "validation_status": "CONFIRMED",
                "lifecycle_status": "OPEN",
            })

        # subprocess.* with shell=True
        if func_name.startswith("subprocess."):
            for kw in node.keywords:
                if kw.arg == "shell" and isinstance(kw.value, ast.Constant) and kw.value.value is True:
                    snippet = self._get_line_snippet(node.lineno)
                    self.findings.append({
                        "fingerprint": generate_fingerprint("bandit", "B602", self.file_path, snippet, node.lineno),
                        "scanner_name": "bandit",
                        "rule_id": "B602",
                        "title": "Subprocess Invoked With shell=True",
                        "message": "subprocess call with shell=True can allow arbitrary command execution if input is not sanitized.",
                        "severity": "HIGH",
                        "confidence": "HIGH",
                        "cwe_id": "CWE-78",
                        "file_path": self.file_path,
                        "start_line": node.lineno,
                        "end_line": getattr(node, "end_lineno", node.lineno),
                        "code_snippet": snippet,
                        "remediation_guidance": "Pass command arguments as a list and set shell=False.",
                        "validation_status": "CONFIRMED",
                        "lifecycle_status": "OPEN",
                    })

        # 2. Check for eval / exec
        if func_name in ("eval", "exec"):
            snippet = self._get_line_snippet(node.lineno)
            self.findings.append({
                "fingerprint": generate_fingerprint("bandit", "B307", self.file_path, snippet, node.lineno),
                "scanner_name": "bandit",
                "rule_id": "B307",
                "title": "Use of Potentially Dangerous Function eval/exec",
                "message": f"Direct execution of code via '{func_name}' can lead to Remote Code Execution.",
                "severity": "CRITICAL",
                "confidence": "HIGH",
                "cwe_id": "CWE-95",
                "file_path": self.file_path,
                "start_line": node.lineno,
                "end_line": getattr(node, "end_lineno", node.lineno),
                "code_snippet": snippet,
                "remediation_guidance": "Refactor logic to use ast.literal_eval or typed parsing instead of dynamic execution.",
                "validation_status": "CONFIRMED",
                "lifecycle_status": "OPEN",
            })

        # 3. Insecure Deserialization: pickle.loads, pickle.load
        if func_name in ("pickle.loads", "pickle.load", "_pickle.loads"):
            snippet = self._get_line_snippet(node.lineno)
            self.findings.append({
                "fingerprint": generate_fingerprint("bandit", "B301", self.file_path, snippet, node.lineno),
                "scanner_name": "bandit",
                "rule_id": "B301",
                "title": "Insecure Deserialization with Pickle",
                "message": "Deserializing untrusted data with pickle can execute arbitrary code.",
                "severity": "CRITICAL",
                "confidence": "HIGH",
                "cwe_id": "CWE-502",
                "file_path": self.file_path,
                "start_line": node.lineno,
                "end_line": getattr(node, "end_lineno", node.lineno),
                "code_snippet": snippet,
                "remediation_guidance": "Use safe data serialization formats like JSON, MessagePack, or Protocol Buffers.",
                "validation_status": "CONFIRMED",
                "lifecycle_status": "OPEN",
            })

        # 4. Weak Cryptography: hashlib.md5 or hashlib.sha1
        if func_name in ("hashlib.md5", "hashlib.sha1"):
            # Check if used_for_security=False is specified
            is_insecure = True
            for kw in node.keywords:
                if kw.arg == "usedforsecurity" and isinstance(kw.value, ast.Constant) and kw.value.value is False:
                    is_insecure = False
            if is_insecure:
                snippet = self._get_line_snippet(node.lineno)
                self.findings.append({
                    "fingerprint": generate_fingerprint("bandit", "B303", self.file_path, snippet, node.lineno),
                    "scanner_name": "bandit",
                    "rule_id": "B303",
                    "title": "Weak Cryptographic Hash Function (MD5/SHA1)",
                    "message": f"Use of insecure cryptographic algorithm '{func_name}'.",
                    "severity": "MEDIUM",
                    "confidence": "HIGH",
                    "cwe_id": "CWE-328",
                    "file_path": self.file_path,
                    "start_line": node.lineno,
                    "end_line": getattr(node, "end_lineno", node.lineno),
                    "code_snippet": snippet,
                    "remediation_guidance": "Upgrade to SHA-256 or SHA-512. For passwords, use Argon2 or bcrypt.",
                    "validation_status": "CONFIRMED",
                    "lifecycle_status": "OPEN",
                })

        # 5. SQL Injection in .execute() calls with formatted strings or string concatenations
        if isinstance(node.func, ast.Attribute) and node.func.attr == "execute":
            if node.args:
                first_arg = node.args[0]
                # Formatted string: f"SELECT ... {var}"
                is_sqli = False
                if isinstance(first_arg, ast.JoinedStr):
                    is_sqli = True
                # Binary operation: "SELECT ... " + var or "SELECT ... %s" % var
                elif isinstance(first_arg, ast.BinOp) and isinstance(first_arg.op, (ast.Add, ast.Mod)):
                    is_sqli = True

                if is_sqli:
                    snippet = self._get_line_snippet(node.lineno)
                    self.findings.append({
                        "fingerprint": generate_fingerprint("bandit", "B608", self.file_path, snippet, node.lineno),
                        "scanner_name": "bandit",
                        "rule_id": "B608",
                        "title": "SQL Injection via String Formatting in Query",
                        "message": "Raw string concatenation or interpolation in SQL execute call.",
                        "severity": "CRITICAL",
                        "confidence": "HIGH",
                        "cwe_id": "CWE-89",
                        "file_path": self.file_path,
                        "start_line": node.lineno,
                        "end_line": getattr(node, "end_lineno", node.lineno),
                        "code_snippet": snippet,
                        "remediation_guidance": "Use parameterized queries or ORM query builders (e.g. cursor.execute(query, (param,)))",
                        "validation_status": "CONFIRMED",
                        "lifecycle_status": "OPEN",
                    })

        self.generic_visit(node)


def scan_python_ast(file_path: str, content: str) -> List[Dict[str, Any]]:
    try:
        tree = ast.parse(content, filename=file_path)
    except SyntaxError:
        # If syntax error in partial diff, skip AST visitor
        return []

    lines = content.splitlines()
    visitor = SecurityASTVisitor(file_path=file_path, source_lines=lines)
    visitor.visit(tree)
    return visitor.findings
