# ADR 0001: Deterministic Scanner Pipeline Preceding AI Triage

## Status
Accepted

## Context
Traditional LLM-based code review platforms suffer from high hallucination rates, fabricated vulnerability identifiers (e.g. non-existent CVEs/CWEs), fluctuating line numbers, and non-deterministic false positives. Furthermore, sending entire massive proprietary codebases to third-party LLMs introduces severe privacy and latency penalties.

## Decision
In Sentinel AI, deterministic security scanners (Python AST analysis matching Bandit patterns, regex entropy secret detectors matching detect-secrets patterns, and standard SARIF parsers) form the foundational layer of analysis.

1. **Deterministic Grounding**: Every security finding must have an unambiguous rule ID, a real line number, a verified code excerpt, and an immutable cryptographic fingerprint.
2. **AI as Triage, Not Scanner**: The AI model only receives the pre-extracted deterministic findings and diff excerpts. It is strictly bounded to summarizing impact, evaluating false positives, and proposing parameterized patches.
3. **SARIF Interchange**: All findings are normalized to OASIS SARIF 2.1.0 specifications for ecosystem compatibility with GitHub Code Scanning and IDE tools.

## Consequences
- **Positive**: 100% reproducible vulnerability findings; verifiable proof of detection; zero fabricated line numbers.
- **Positive**: Works offline without any paid LLM API key.
- **Negative**: Scanners only detect patterns defined in their deterministic rule trees.
