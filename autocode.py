#!/usr/bin/env python3
"""AutoCode Router: choose local Ollama or Claude Code for a coding task."""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass, asdict

HARD_TERMS = {
    "architecture": 3,
    "architect": 3,
    "security": 3,
    "vulnerability": 4,
    "migration": 3,
    "refactor": 2,
    "debug": 2,
    "race condition": 4,
    "concurrency": 3,
    "distributed": 3,
    "production": 2,
    "database migration": 4,
    "performance": 2,
    "benchmark": 2,
    "multi-file": 3,
    "repo-wide": 4,
    "review": 2,
    "verify": 2,
    "tests failing": 3,
    "root cause": 3,
}


@dataclass
class Decision:
    backend: str
    score: int
    threshold: int
    reasons: list[str]
    local_model: str


def complexity_score(prompt: str) -> tuple[int, list[str]]:
    text = prompt.lower()
    score = 0
    reasons: list[str] = []

    n = len(prompt)
    if n > 800:
        score += 2
        reasons.append("long prompt")
    if n > 2500:
        score += 2
        reasons.append("very long prompt")
    if prompt.count("\n") >= 8:
        score += 1
        reasons.append("multi-part task")

    matched = []
    for term, weight in HARD_TERMS.items():
        if term in text:
            score += weight
            matched.append(term)
    if matched:
        reasons.append("complexity terms: " + ", ".join(matched[:5]))

    if any(x in text for x in ("quick", "fast", "simple", "small change", "typo")):
        score -= 2
        reasons.append("speed/simple cue")

    return max(score, 0), reasons or ["routine task"]


def decide(prompt: str, mode: str, threshold: int, local_model: str) -> Decision:
    score, reasons = complexity_score(prompt)
    if mode == "local":
        backend = "local"
        reasons = ["forced local"] + reasons
    elif mode == "cloud":
        backend = "cloud"
        reasons = ["forced cloud"] + reasons
    elif mode == "fast":
        backend = "local" if score < max(threshold + 2, 1) else "cloud"
        reasons = ["speed-biased routing"] + reasons
    elif mode == "quality":
        backend = "cloud" if score >= max(threshold - 2, 0) else "local"
        reasons = ["quality-biased routing"] + reasons
    else:
        backend = "cloud" if score >= threshold else "local"
    return Decision(backend, score, threshold, reasons, local_model)


def ensure_command(name: str) -> None:
    if not shutil.which(name):
        raise SystemExit(f"Required command not found: {name}")


def run(decision: Decision, prompt: str | None, passthrough: list[str]) -> int:
    ensure_command("claude")
    env = os.environ.copy()
    cmd = ["claude"]

    if decision.backend == "local":
        if not shutil.which("ollama"):
            raise SystemExit("Local route selected but Ollama is not installed.")
        env["ANTHROPIC_AUTH_TOKEN"] = "ollama"
        env["ANTHROPIC_API_KEY"] = ""
        env["ANTHROPIC_BASE_URL"] = "http://127.0.0.1:11434"
        cmd += ["--model", decision.local_model]
    else:
        for key in ("ANTHROPIC_AUTH_TOKEN", "ANTHROPIC_BASE_URL"):
            env.pop(key, None)

    if prompt:
        cmd += ["-p", prompt]
    cmd += passthrough
    return subprocess.call(cmd, env=env)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="autocode",
        description="Route Claude Code tasks between local Ollama and Anthropic Claude.",
    )
    p.add_argument("prompt", nargs="?", help="Coding task. Omit for interactive Claude Code.")
    p.add_argument("--mode", choices=["auto", "fast", "quality", "local", "cloud"], default="auto")
    p.add_argument("--local-model", default=os.getenv("AUTOCODE_LOCAL_MODEL", "qwen3.5:27b"))
    p.add_argument("--threshold", type=int, default=int(os.getenv("AUTOCODE_THRESHOLD", "5")))
    p.add_argument("--explain", action="store_true", help="Explain the routing decision before running.")
    p.add_argument("--json", action="store_true", help="Print routing decision as JSON and exit.")
    p.add_argument("--dry-run", action="store_true", help="Print routing decision and exit without launching Claude Code.")
    return p


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    passthrough: list[str] = []
    if "--" in argv:
        i = argv.index("--")
        passthrough = argv[i + 1 :]
        argv = argv[:i]

    args = build_parser().parse_args(argv)
    prompt = args.prompt or ""
    decision = decide(prompt, args.mode, args.threshold, args.local_model)

    if args.json:
        print(json.dumps(asdict(decision), indent=2))
        return 0
    if args.explain or args.dry_run:
        model = decision.local_model if decision.backend == "local" else "Claude"
        print(f"route={decision.backend} score={decision.score}/{decision.threshold} model={model}")
        print("reason=" + "; ".join(decision.reasons))
    if args.dry_run:
        return 0
    return run(decision, args.prompt, passthrough)


if __name__ == "__main__":
    raise SystemExit(main())
