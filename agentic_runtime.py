from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

from src.orchestrator import AgenticOrchestrator
from src.tools import list_scenarios


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Run P6 agentic orchestrator scenarios.")
    p.add_argument("--scenario", default="all", help="Scenario incident_id or 'all'")
    p.add_argument("--use-llm", action="store_true", help="Enable Vocareum/OpenAI-compatible LLM enrichment")
    p.add_argument("--model", default="gpt-4o-mini", help="Model name when --use-llm is enabled")
    p.add_argument("--output-dir", default="outputs", help="Output directory for logs/artifacts")
    p.add_argument("--reset-output", action="store_true", help="Delete output-dir before running for a clean run")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    out_dir = Path(args.output_dir)
    if args.reset_output and out_dir.exists():
        shutil.rmtree(out_dir)

    orchestrator = AgenticOrchestrator(output_dir=out_dir, use_llm=args.use_llm, model=args.model)

    if args.scenario.lower() == "all":
        incident_ids = list_scenarios()
    else:
        incident_ids = [args.scenario]

    results = orchestrator.run_many(incident_ids)

    llm_debug = {}
    try:
        llm_debug = orchestrator.rca.llm.debug_status()  # type: ignore[attr-defined]
    except Exception:
        llm_debug = {"enabled": bool(args.use_llm), "debug_status_available": False}

    llm_calls_path = out_dir / "llm_calls.jsonl"
    llm_calls_count = 0
    if llm_calls_path.exists():
        llm_calls_count = sum(1 for _ in llm_calls_path.open("r", encoding="utf-8"))

    summary = {
        "run_count": len(results),
        "incident_ids": [r["incident_id"] for r in results],
        "decision_types": {k: sum(1 for r in results if r["decision_type"] == k) for k in ["propose", "escalate", "refuse", "defer"]},
        "escalation_rate": round(sum(1 for r in results if r["escalation_required"]) / max(len(results), 1), 4),
        "policy_pass_rate": round(sum(1 for r in results if r.get("policy_passed")) / max(len(results), 1), 4),
        "mean_evidence_quality": round(sum(float(r.get("evidence_quality", 0.0)) for r in results) / max(len(results), 1), 4),
        "mean_hypothesis_confidence": round(
            sum(float(r.get("selected_hypothesis_confidence", 0.0)) for r in results) / max(len(results), 1), 4
        ),
        "zones": sorted({str(r.get("zone")) for r in results if r.get("zone") is not None}),
        "nist_watch_count": sum(
            1
            for r in results
            for f in (r.get("nist_findings") or [])
            if str(f.get("status", "")).lower() == "watch"
        ),
        "iec_watch_count": sum(
            1
            for r in results
            for f in (r.get("iec_findings") or [])
            if str(f.get("status", "")).lower() == "watch"
        ),
        "llm_runtime": {
            "arg_use_llm": bool(args.use_llm),
            "model": args.model,
            "debug": llm_debug,
            "llm_calls_file_exists": llm_calls_path.exists(),
            "llm_calls_count": llm_calls_count,
        },
    }

    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "run_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    print("Run summary:")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
