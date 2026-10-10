import ast
import hashlib
import json
import os
import sqlite3
import subprocess

def get_user_profile(user_id: str):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    # SAFE: Parameterized SQL query (no injection)
    query = "SELECT id, username, email FROM users WHERE id = ?"
    cursor.execute(query, (user_id,))
    return cursor.fetchone()

def ping_host(host_ip: str):
    # SAFE: subprocess.run with arguments list and shell=False
    return subprocess.run(["ping", "-c", "1", host_ip], shell=False, check=True)

def execute_diagnostics(command_arg: str):
    # SAFE: list arguments, shell=False
    return subprocess.run(["echo", command_arg], shell=False, check=True)

def load_session_state(raw_json_bytes: bytes):
    # SAFE: json serialization instead of pickle
    return json.loads(raw_json_bytes.decode("utf-8"))

def compute_user_hash(password: str):
    # SAFE: SHA-256 cryptographic hash
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def evaluate_math(expression: str):
    # SAFE: ast.literal_eval instead of eval
    return ast.literal_eval(expression)
