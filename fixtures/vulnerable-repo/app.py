import hashlib
import os
import pickle
import subprocess
import sqlite3

def get_user_profile(user_id: str):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    # VULNERABILITY: SQL Injection via formatted string (CWE-89)
    query = f"SELECT id, username, email FROM users WHERE id = '{user_id}'"
    cursor.execute(query)
    return cursor.fetchone()

def ping_host(host_ip: str):
    # VULNERABILITY: Command Injection via os.system (CWE-78)
    cmd = f"ping -c 1 {host_ip}"
    return os.system(cmd)

def execute_diagnostics(command_arg: str):
    # VULNERABILITY: Command Injection via subprocess with shell=True (CWE-78)
    return subprocess.run(f"echo {command_arg}", shell=True)

def load_session_state(raw_cookie_bytes: bytes):
    # VULNERABILITY: Insecure Deserialization via pickle (CWE-502)
    return pickle.loads(raw_cookie_bytes)

def compute_user_hash(password: str):
    # VULNERABILITY: Weak Cryptographic Hash MD5 (CWE-328)
    return hashlib.md5(password.encode()).hexdigest()

def evaluate_math(expression: str):
    # VULNERABILITY: Dangerous eval (CWE-95)
    return eval(expression)
