"""Detect likely architecture drift with conservative repository heuristics.

This v1 prefers structured, explainable findings over deep inference. It reports
`confirmed`, `probable`, and `unknown` categories in JSON so both humans and agents
can consume the result predictably.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

from _common import discover_diagrams, iter_text_files, read_text, resolve_root


RESOURCE_PATTERNS: dict[str, tuple[re.Pattern[str], str]] = {
    "queue": (re.compile(r"\b(aws_sqs_queue|queue|dead[_ -]?letter|kafka|rabbitmq|topic)\b", re.IGNORECASE), "strong"),
    "bucket": (re.compile(r"\b(bucket|aws_s3_bucket|s3|gcs)\b", re.IGNORECASE), "strong"),
    "database": (re.compile(r"\b(postgres|mysql|mongodb|redis|database|db_name|connection_string)\b", re.IGNORECASE), "strong"),
    "worker": (re.compile(r"\b(worker|workers|job|jobs|cron|scheduler|lambda|serverless)\b", re.IGNORECASE), "weak"),
    "gateway": (re.compile(r"\b(api gateway|ingress|gateway|reverse proxy|public api|graphql)\b", re.IGNORECASE), "strong"),
    "external_service": (re.compile(r"\b(stripe|sendgrid|twilio|slack|salesforce)\b", re.IGNORECASE), "weak"),
}
EXTERNAL_SERVICE_NAMES = ("stripe", "sendgrid", "twilio", "slack", "salesforce")


@dataclass(slots=True)
class Finding:
    category: str
    resource_type: str
    message: str
    evidence: list[str]


def _normalize(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()


def diagram_corpus(root: Path) -> str:
    parts: list[str] = []
    for path in discover_diagrams(root):
        parts.append(read_text(path))
    return _normalize("\n".join(parts))


def infer_findings(root: Path) -> dict[str, list[Finding]]:
    corpus = diagram_corpus(root)
    findings: dict[str, list[Finding]] = {"confirmed": [], "probable": [], "unknown": []}
    diagram_count = len(discover_diagrams(root))

    for file_path in iter_text_files(root):
        try:
            content = read_text(file_path)
        except UnicodeDecodeError:
            continue
        snippet = content[:4000]
        normalized_file = _normalize(f"{file_path.name} {snippet}")
        for resource_type, (pattern, strength) in RESOURCE_PATTERNS.items():
            if not pattern.search(snippet):
                continue
            if resource_type == "external_service":
                if any(name in _normalize(snippet) and name in corpus for name in EXTERNAL_SERVICE_NAMES):
                    continue
            diagram_mentions_type = resource_type.replace("_", " ") in corpus
            evidence = [str(file_path)]
            if diagram_count == 0 and strength == "strong":
                findings["confirmed"].append(
                    Finding(
                        category="confirmed",
                        resource_type=resource_type,
                        message=f"Strong {resource_type} evidence exists in the repository but no architecture diagrams were found.",
                        evidence=evidence,
                    )
                )
            elif strength == "strong" and not diagram_mentions_type:
                findings["probable"].append(
                    Finding(
                        category="probable",
                        resource_type=resource_type,
                        message=f"Strong {resource_type} evidence exists but the current diagrams do not mention that resource type.",
                        evidence=evidence,
                    )
                )
            elif strength == "weak" and resource_type.replace("_", " ") not in corpus and normalized_file:
                findings["unknown"].append(
                    Finding(
                        category="unknown",
                        resource_type=resource_type,
                        message=f"Weak heuristic suggests {resource_type} may matter architecturally; human review is recommended.",
                        evidence=evidence,
                    )
                )

    for key in findings:
        deduped: dict[tuple[str, str, tuple[str, ...]], Finding] = {}
        for finding in findings[key]:
            deduped[(finding.resource_type, finding.message, tuple(finding.evidence))] = finding
        findings[key] = list(deduped.values())
    return findings


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Detect likely architecture drift and emit structured JSON.")
    parser.add_argument("--root", required=True, help="Path to the target repository root.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        root = resolve_root(args.root)
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    findings = infer_findings(root)
    payload = {
        "confirmed": [asdict(item) for item in findings["confirmed"]],
        "probable": [asdict(item) for item in findings["probable"]],
        "unknown": [asdict(item) for item in findings["unknown"]],
        "limitations": [
            "v1 uses repository heuristics and does not parse infrastructure providers exhaustively.",
            "v1 only compares inferred resource types against current diagram text, not full semantic topology.",
        ],
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
