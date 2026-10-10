from typing import Any, Dict, List


SEVERITY_TO_SARIF_LEVEL = {
    "CRITICAL": "error",
    "HIGH": "error",
    "MEDIUM": "warning",
    "LOW": "note",
    "INFORMATIONAL": "note",
}


def export_to_sarif(findings: List[Dict[str, Any]], run_id: str = "sentinel-scan") -> Dict[str, Any]:
    """
    Export normalized Sentinel findings to standard SARIF 2.1.0 format.
    """
    rules_dict: Dict[str, Dict[str, Any]] = {}
    results: List[Dict[str, Any]] = []

    for f in findings:
        rule_id = f.get("rule_id", "GENERIC-001")
        if rule_id not in rules_dict:
            rules_dict[rule_id] = {
                "id": rule_id,
                "name": f.get("title", rule_id),
                "shortDescription": {
                    "text": f.get("title", rule_id)
                },
                "fullDescription": {
                    "text": f.get("message", "")
                },
                "help": {
                    "text": f.get("remediation_guidance", "Review security recommendation.")
                },
                "properties": {
                    "precision": "high",
                    "security-severity": "8.0" if f.get("severity") in ("CRITICAL", "HIGH") else "5.0",
                    "cwe": [f.get("cwe_id")] if f.get("cwe_id") else []
                }
            }

        level = SEVERITY_TO_SARIF_LEVEL.get(f.get("severity", "MEDIUM"), "warning")
        
        result_entry = {
            "ruleId": rule_id,
            "level": level,
            "message": {
                "text": f.get("message", "")
            },
            "locations": [
                {
                    "physicalLocation": {
                        "artifactLocation": {
                            "uri": f.get("file_path", "").replace("\\", "/")
                        },
                        "region": {
                            "startLine": f.get("start_line", 1),
                            "endLine": f.get("end_line", 1),
                            "snippet": {
                                "text": f.get("code_snippet", "")
                            }
                        }
                    }
                }
            ],
            "fingerprints": {
                "sentinelFingerprint/v1": f.get("fingerprint", "")
            },
            "properties": {
                "cwe": f.get("cwe_id"),
                "confidence": f.get("confidence", "HIGH"),
                "scannerName": f.get("scanner_name", "sentinel-engine")
            }
        }
        results.append(result_entry)

    return {
        "$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json",
        "version": "2.1.0",
        "runs": [
            {
                "tool": {
                    "driver": {
                        "name": "Sentinel AI Security Engine",
                        "version": "1.0.0",
                        "informationUri": "https://github.com/sentinel-ai/sentinel",
                        "rules": list(rules_dict.values())
                    }
                },
                "results": results
            }
        ]
    }
