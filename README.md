# Agentic AI Cybersecurity Workflow (P6)

## Project Description
This project implements a multi-agent cybersecurity workflow for IIoT/OT incident triage and RCA support. The system uses one orchestrator and five role agents (intake, evidence, RCA, response planning, governance), integrates optional LLM refinement via a Vocareum-compatible endpoint, and enforces NIST/IEC-oriented governance checks before final decision output.

## Project Repository
- https://github.com/Ohara124c41/agentic-ai-mitre-attack-rca.git

## What I Built
- `agentic_system.ipynb`: end-to-end reviewer-facing notebook (execution, EDA, analysis, V&V, fairness screening)
- `agentic_runtime.py`: script-first orchestrator runner
- `src/`: modular orchestrator, agents, tools, schemas, and LLM client
- `ARCHITECTURE.md`: system architecture and component flow
- `Agentic_AI_System_Design_Report_draft.md`: report draft with citations
- `requirements.txt`: minimal reproducibility dependencies

## Dataset and Knowledge Sources
- Incident scenario dataset: `data/scenarios.json`
- MITRE ATT&CK Enterprise STIX:
  - https://github.com/mitre/cti/tree/master/enterprise-attack
- NIST CSF 2.0:
  - https://www.nist.gov/cyberframework

## How To Run
1. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure credentials (optional, for LLM-enabled mode):
- Copy `.env.example` to `.env`
- Set:
  - `VOCAREUM_API_KEY`
  - `VOCAREUM_API_BASE` (default: `https://openai.vocareum.com/v1`)

4. Run notebook workflow:
```bash
jupyter notebook
```
- Open `agentic_system.ipynb`
- Run cells top-to-bottom

5. Or run script-first workflow:
```bash
python agentic_runtime.py --scenario all --output-dir outputs --reset-output
```
- Add LLM mode:
```bash
python agentic_runtime.py --scenario all --output-dir outputs --reset-output --use-llm --model gpt-4o-mini
```

## Key Output Artifacts
- `outputs/run_summary.json`
- `outputs/decision_packets.jsonl`
- `outputs/audit_log.jsonl`
- `outputs/llm_calls.jsonl` (when LLM mode is enabled)
- `outputs/state_snapshots/*.json`
- `outputs/artifacts/incident_embeddings.npz`
- `outputs/artifacts/embedding_retrieval_top2.json`
- `outputs/models/agent_policy_snapshot.json`
- `debug/llm_connectivity_check.json`

## Reproducibility Notes
- Notebook and runtime use the same scenario source (`data/scenarios.json`) and output schema.
- MITRE ATT&CK STIX is auto-downloaded to cache under `data/external/` if not present.
- LLM usage is explicitly logged and summarized through `llm_runtime` fields in `run_summary.json`.
- The notebook includes deterministic fallback behavior when LLM credentials are unavailable.

## Evaluation Highlights (Current Run)
- `run_count = 5`
- `decision_types = {escalate: 4, refuse: 1, propose: 0, defer: 0}`
- `policy_pass_rate = 0.4`
- `mean_evidence_quality = 0.74`
- `mean_hypothesis_confidence = 0.8187`
- LLM-enabled runtime confirmed (`llm_calls_count = 5`)

## Sections Covered in Notebook and Report
- Overview and motivation
- Task/use-case definition and scope
- Agent architecture and workflow design
- Persona/reasoning/decision logic
- Tool use and memory/state design
- Evaluation of behavior with plots and case-level artifacts
- NIST/IEC governance checks (V&V)
- Fairness-risk audit (AIF360-compatible workflow)
- Limitations, safeguards, and future improvements
- References with in-text citation coverage
