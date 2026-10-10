import os

# SAFE: All secrets and credentials retrieved strictly from environment variables
AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
DATABASE_URL = os.environ.get("DATABASE_URL")
SLACK_WEBHOOK = os.environ.get("SLACK_WEBHOOK_URL")
