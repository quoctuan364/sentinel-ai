# Contributing to Sentinel AI

Thank you for your interest in contributing to Sentinel AI!

## Code of Conduct
We are committed to providing a friendly, safe, and welcoming environment for all contributors.

## Local Development Workflow

### Prerequisites
- Python 3.10+
- Node.js 18+ (20+ recommended)
- Docker & Docker Compose (optional for full containerized stack)

### 1. Backend Setup
```bash
python -m venv services/api/.venv
# Windows:
.\services\api\.venv\Scripts\activate
# Linux/macOS:
source services/api/.venv/bin/activate

pip install -r services/api/requirements.txt
pip install email-validator aiosqlite
```

Run tests:
```bash
pytest -v
```

Start API:
```bash
uvicorn app.main:app --reload --port 8000
```

### 2. Frontend Setup
```bash
cd apps/web
npm install
npm run dev
```

### 3. Running Scans Locally
You can trigger security scans directly from the UI or via REST API against `./fixtures/vulnerable-repo` without needing GitHub credentials or an LLM API key.

## Security Disclosures
If you discover a security vulnerability in Sentinel AI itself, please email `security@sentinel.ai` instead of opening a public issue.
