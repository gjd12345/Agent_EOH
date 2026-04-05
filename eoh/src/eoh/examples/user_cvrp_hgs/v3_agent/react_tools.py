import os
import sys
import json
import datetime
from typing import Any, Dict, Optional

src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
example_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if src_path not in sys.path:
    sys.path.insert(0, src_path)
if example_root not in sys.path:
    sys.path.insert(0, example_root)

import v2_agent.react_tools as _base
from v3_agent.dataset_collector import collector as _dataset_collector

_V3_DIR = os.path.dirname(os.path.abspath(__file__))
_STATE_DIR = os.path.join(_V3_DIR, "state")
_LOG_DIR = os.path.join(_V3_DIR, "logs")

TASKS_PATH = os.path.join(_STATE_DIR, "tasks.json")
PROJECT_TRUTH_PATH = os.path.join(_STATE_DIR, "project_truth.md")
SESSION_CONTEXT_PATH = os.path.join(_STATE_DIR, "session_context.md")

EVOLUTION_LEDGER_PATH = os.path.join(_LOG_DIR, "evolution_ledger.jsonl")
REVIEW_LOG_PATH = os.path.join(_LOG_DIR, "review_log.md")

_base.__file__ = __file__
_V3_CONFIG_PATH = os.path.join(_V3_DIR, "config.json")
_V2_CONFIG_FALLBACK_PATH = os.path.abspath(os.path.join(_V3_DIR, "..", "v2_agent", "config.json"))
_base.CONFIG_PATH = _V3_CONFIG_PATH if os.path.exists(_V3_CONFIG_PATH) else _V2_CONFIG_FALLBACK_PATH
_base.dataset_collector = _dataset_collector


def _now_iso() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def _ensure_dirs() -> None:
    os.makedirs(_STATE_DIR, exist_ok=True)
    os.makedirs(_LOG_DIR, exist_ok=True)


def _default_tasks() -> Dict[str, Any]:
    now = _now_iso()
    stages = [
        {
            "stageId": "survey",
            "title": "Survey (SOTA/targets)",
            "status": "todo",
            "qualityGate": {
                "description": "Targets and evidence are traceable, with clear evaluation protocol.",
                "criteria": [
                    "instances and metrics are defined",
                    "BKS/lower bounds are recorded with sources",
                    "baseline operators/seeds are shortlisted"
                ]
            },
            "tasks": [
                {
                    "taskId": "SURVEY-001",
                    "title": "Define target instances and evaluation protocol",
                    "status": "todo",
                    "priority": "high",
                    "ownerRole": "master",
                    "outputs": [],
                    "dependsOn": [],
                    "relatedRuns": [],
                    "createdAt": now,
                    "updatedAt": now,
                    "notes": ""
                },
                {
                    "taskId": "SURVEY-002",
                    "title": "Collect BKS/lower bounds and baseline operators",
                    "status": "todo",
                    "priority": "high",
                    "ownerRole": "librarian",
                    "outputs": [],
                    "dependsOn": ["SURVEY-001"],
                    "relatedRuns": [],
                    "createdAt": now,
                    "updatedAt": now,
                    "notes": ""
                }
            ]
        },
        {
            "stageId": "design",
            "title": "Design (PRM/constraints)",
            "status": "todo",
            "qualityGate": {
                "description": "PRM and constraints are defined with reviewer-passable injection contract.",
                "criteria": [
                    "PRM injection contract is documented",
                    "seed admission criteria are defined",
                    "failure-mode playbook exists (none_rate/tracebacks)"
                ]
            },
            "tasks": [
                {
                    "taskId": "DESIGN-001",
                    "title": "Define PRM injection contract and constraints",
                    "status": "todo",
                    "priority": "high",
                    "ownerRole": "architect",
                    "outputs": [],
                    "dependsOn": ["SURVEY-002"],
                    "relatedRuns": [],
                    "createdAt": now,
                    "updatedAt": now,
                    "notes": ""
                },
                {
                    "taskId": "DESIGN-002",
                    "title": "Define seed strategy and admission criteria",
                    "status": "todo",
                    "priority": "medium",
                    "ownerRole": "reviewer",
                    "outputs": [],
                    "dependsOn": ["SURVEY-002"],
                    "relatedRuns": [],
                    "createdAt": now,
                    "updatedAt": now,
                    "notes": ""
                }
            ]
        },
        {
            "stageId": "evolve",
            "title": "Evolve (EoH runs)",
            "status": "todo",
            "qualityGate": {
                "description": "Runs are ledgered and best code/trajectory is traceable by runId.",
                "criteria": [
                    "each evolution run has a ledger record",
                    "trajectory and best code paths are recorded",
                    "plateau/none_rate rules are available"
                ]
            },
            "tasks": [
                {
                    "taskId": "EVOLVE-001",
                    "title": "Run baseline evolution and log the first run",
                    "status": "todo",
                    "priority": "high",
                    "ownerRole": "master",
                    "outputs": [],
                    "dependsOn": ["DESIGN-001"],
                    "relatedRuns": [],
                    "createdAt": now,
                    "updatedAt": now,
                    "notes": ""
                },
                {
                    "taskId": "EVOLVE-002",
                    "title": "Define plateau/none_rate decision rules",
                    "status": "todo",
                    "priority": "medium",
                    "ownerRole": "analyst",
                    "outputs": [],
                    "dependsOn": ["EVOLVE-001"],
                    "relatedRuns": [],
                    "createdAt": now,
                    "updatedAt": now,
                    "notes": ""
                }
            ]
        },
        {
            "stageId": "validate",
            "title": "Validate (QC/robustness)",
            "status": "todo",
            "qualityGate": {
                "description": "Cross-instance validation passes and reviewer gates are documented with evidence.",
                "criteria": [
                    "review_log has pass/fail traceability",
                    "comprehensive evaluation covers target instances",
                    "regression comparison exists for best candidate"
                ]
            },
            "tasks": [
                {
                    "taskId": "VALIDATE-001",
                    "title": "Define and apply code review gate before saving seeds",
                    "status": "todo",
                    "priority": "high",
                    "ownerRole": "reviewer",
                    "outputs": [],
                    "dependsOn": ["EVOLVE-001"],
                    "relatedRuns": [],
                    "createdAt": now,
                    "updatedAt": now,
                    "notes": ""
                },
                {
                    "taskId": "VALIDATE-002",
                    "title": "Run cross-instance evaluation and summarize results",
                    "status": "todo",
                    "priority": "high",
                    "ownerRole": "analyst",
                    "outputs": [],
                    "dependsOn": ["EVOLVE-001"],
                    "relatedRuns": [],
                    "createdAt": now,
                    "updatedAt": now,
                    "notes": ""
                }
            ]
        },
        {
            "stageId": "package",
            "title": "Package (report/deploy/paper assets)",
            "status": "todo",
            "qualityGate": {
                "description": "Report, visuals, and deployable module are produced and reproducible.",
                "criteria": [
                    "visual report paths are recorded",
                    "deployment module exists with usage notes",
                    "paper-ready claims and caveats are captured"
                ]
            },
            "tasks": [
                {
                    "taskId": "PKG-001",
                    "title": "Generate visual report and link artifacts",
                    "status": "todo",
                    "priority": "medium",
                    "ownerRole": "visualizer",
                    "outputs": [],
                    "dependsOn": ["VALIDATE-002"],
                    "relatedRuns": [],
                    "createdAt": now,
                    "updatedAt": now,
                    "notes": ""
                },
                {
                    "taskId": "PKG-002",
                    "title": "Deploy best algorithm as module with usage docs",
                    "status": "todo",
                    "priority": "medium",
                    "ownerRole": "deployer",
                    "outputs": [],
                    "dependsOn": ["VALIDATE-002"],
                    "relatedRuns": [],
                    "createdAt": now,
                    "updatedAt": now,
                    "notes": ""
                }
            ]
        }
    ]
    return {
        "schemaVersion": "1.0",
        "project": {
            "name": "user_cvrp_hgs",
            "domain": "CVRP+EoH",
            "createdAt": now,
            "updatedAt": now
        },
        "currentStage": "survey",
        "activeTaskId": "SURVEY-001",
        "stages": stages
    }


def _read_json(path: str) -> Any:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _write_json(path: str, data: Any) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def sync_state() -> str:
    """
    Ensures v3_agent state/log directories and baseline files exist.
    Regenerates session_context.md from tasks.json and recent ledger.
    """
    _ensure_dirs()
    if not os.path.exists(TASKS_PATH):
        _write_json(TASKS_PATH, _default_tasks())
    if not os.path.exists(PROJECT_TRUTH_PATH):
        with open(PROJECT_TRUTH_PATH, "w", encoding="utf-8") as f:
            f.write("# Project Truth\n\n")
            f.write("## Research Goal\n- \n\n")
            f.write("## Evaluation Protocol (Engineering)\n- instances:\n- metric:\n- runtime budget:\n- randomness seed policy:\n\n")
            f.write("## Progress Log (Engineering Facts)\n\n")
            f.write("## Paper Notes (Research Narrative)\n\n")
    if not os.path.exists(EVOLUTION_LEDGER_PATH):
        with open(EVOLUTION_LEDGER_PATH, "a", encoding="utf-8") as f:
            f.write("")
    if not os.path.exists(REVIEW_LOG_PATH):
        with open(REVIEW_LOG_PATH, "a", encoding="utf-8") as f:
            f.write("")
    _write_session_context()
    return "v3_agent state synchronized."


def read_tasks() -> str:
    """Reads v3_agent/state/tasks.json for planning and task selection."""
    sync_state()
    return json.dumps(_read_json(TASKS_PATH), ensure_ascii=False, indent=2)


def set_active_task(task_id: str, stage: Optional[str] = None) -> str:
    """Sets tasks.json.activeTaskId (and optionally currentStage), then refreshes session_context.md."""
    sync_state()
    tasks = _read_json(TASKS_PATH)
    tasks["activeTaskId"] = task_id
    if stage is not None:
        tasks["currentStage"] = stage
    tasks["project"]["updatedAt"] = _now_iso()
    _write_json(TASKS_PATH, tasks)
    _write_session_context()
    return f"Active task set to {task_id}."


def update_task_status(task_id: str, status: str, notes: str = "") -> str:
    """Updates a task status in tasks.json and refreshes session_context.md."""
    sync_state()
    tasks = _read_json(TASKS_PATH)
    now = _now_iso()
    updated = False
    for st in tasks.get("stages", []):
        for t in st.get("tasks", []):
            if t.get("taskId") == task_id:
                t["status"] = status
                if notes:
                    t["notes"] = notes
                t["updatedAt"] = now
                updated = True
                break
        if updated:
            break
    if not updated:
        return f"Task not found: {task_id}"
    tasks["project"]["updatedAt"] = now
    _write_json(TASKS_PATH, tasks)
    _write_session_context()
    return f"Task {task_id} updated to status={status}."


def read_session_context() -> str:
    """Reads v3_agent/state/session_context.md."""
    sync_state()
    with open(SESSION_CONTEXT_PATH, "r", encoding="utf-8") as f:
        return f.read()


def append_project_truth_fact(
    summary: Optional[str] = None,
    fact: Optional[str] = None,
    stage: Optional[str] = None,
    task_id: Optional[str] = None,
    run_id: Optional[str] = None,
    metrics: Optional[Dict[str, Any]] = None,
    artifacts: Optional[Dict[str, Any]] = None,
    decision: Optional[str] = None,
    next_step: Optional[str] = None,
    **kwargs,
) -> str:
    """Appends an engineering-facts entry to project_truth.md."""
    if summary is None:
        summary = fact
    if summary is None:
        summary = kwargs.get("message") or kwargs.get("text")
    if not summary:
        return "Project truth update skipped: missing summary."
    sync_state()
    tasks = _read_json(TASKS_PATH)
    st = stage or tasks.get("currentStage")
    tid = task_id or tasks.get("activeTaskId")
    entry = []
    entry.append(f"- time: {_now_iso()}")
    entry.append(f"  stage: {st}")
    if tid:
        entry.append(f"  task: {tid}")
    if run_id:
        entry.append(f"  run: {run_id}")
    entry.append(f"  summary: {summary}")
    if metrics:
        entry.append(f"  metrics: {json.dumps(metrics, ensure_ascii=False)}")
    if artifacts:
        entry.append(f"  artifacts: {json.dumps(artifacts, ensure_ascii=False)}")
    if decision:
        entry.append(f"  decision: {decision}")
    if next_step:
        entry.append(f"  next: {next_step}")
    entry.append("")
    with open(PROJECT_TRUTH_PATH, "r", encoding="utf-8") as f:
        content = f.read()
    marker = "## Paper Notes (Research Narrative)\n"
    if marker not in content:
        return "project_truth.md is missing required sections."
    before, after = content.split(marker, 1)
    if "## Progress Log (Engineering Facts)\n" not in before:
        return "project_truth.md is missing Progress Log section."
    before = before.rstrip() + "\n" + "\n".join(entry) + "\n"
    with open(PROJECT_TRUTH_PATH, "w", encoding="utf-8") as f:
        f.write(before + marker + after)
    return "Project truth (facts) updated."


def append_project_truth_paper(
    claim: Optional[str] = None,
    evidence: Optional[str] = None,
    caveat: str = "",
    writing_ready: str = "",
    stage: Optional[str] = None,
    task_id: Optional[str] = None,
    run_id: Optional[str] = None,
    **kwargs,
) -> str:
    """Appends a paper-facing entry to project_truth.md."""
    if claim is None:
        claim = kwargs.get("summary") or kwargs.get("text")
    if evidence is None:
        evidence = kwargs.get("evidence") or kwargs.get("source") or ""
    if not claim:
        return "Project truth paper-note skipped: missing claim."
    if not evidence:
        evidence = "N/A"
    sync_state()
    tasks = _read_json(TASKS_PATH)
    st = stage or tasks.get("currentStage")
    tid = task_id or tasks.get("activeTaskId")
    lines = []
    lines.append(f"- time: {_now_iso()}")
    lines.append(f"  stage: {st}")
    if tid:
        lines.append(f"  task: {tid}")
    if run_id:
        lines.append(f"  run: {run_id}")
    lines.append(f"  claim: {claim}")
    lines.append(f"  evidence: {evidence}")
    if caveat:
        lines.append(f"  caveat: {caveat}")
    if writing_ready:
        lines.append(f"  writing-ready: \"{writing_ready}\"")
    lines.append("")
    with open(PROJECT_TRUTH_PATH, "a", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    return "Project truth (paper notes) updated."


def _get_latest_run_id() -> str:
    try:
        if not os.path.exists(EVOLUTION_LEDGER_PATH):
            return ""
        with open(EVOLUTION_LEDGER_PATH, "r", encoding="utf-8") as f:
            lines = [ln for ln in f.read().splitlines() if ln.strip()]
        if not lines:
            return ""
        last = json.loads(lines[-1])
        return last.get("runId", "")
    except Exception:
        return ""


def _write_session_context() -> None:
    tasks = _read_json(TASKS_PATH)
    stage = tasks.get("currentStage", "unknown")
    active_task = tasks.get("activeTaskId", "")
    run_id = _get_latest_run_id()
    lines = []
    lines.append("# Session Context (Auto-generated)")
    lines.append("")
    lines.append("## Current")
    lines.append(f"- stage: {stage}")
    if active_task:
        lines.append(f"- active_task: {active_task}")
    if run_id:
        lines.append(f"- last_run: {run_id}")
    lines.append("")
    lines.append("## Next Actions (menu)")
    lines.append("1) read_tasks")
    lines.append("2) set_active_task")
    lines.append("3) run_evolution")
    lines.append("4) analyze_latest_results")
    lines.append("5) run_code_review")
    lines.append("6) run_deep_analysis")
    lines.append("7) run_comprehensive_evaluation")
    lines.append("")
    lines.append(f"_generatedAt: {_now_iso()}_")
    with open(SESSION_CONTEXT_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def _new_run_id() -> str:
    ts = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")
    prefix = f"RUN-{ts}-"
    existing = 0
    try:
        if os.path.exists(EVOLUTION_LEDGER_PATH):
            with open(EVOLUTION_LEDGER_PATH, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip().startswith("{") and prefix in line:
                        existing += 1
    except Exception:
        existing = 0
    return f"{prefix}{existing+1:03d}"


def _append_evolution_ledger(record: Dict[str, Any]) -> None:
    with open(EVOLUTION_LEDGER_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def _append_review_log(task_id: str, verdict: str, risks: list, notes: str = "", code_hash: str = "") -> None:
    with open(REVIEW_LOG_PATH, "a", encoding="utf-8") as f:
        f.write(f"## Review: {task_id} / code={code_hash}\n")
        f.write(f"- verdict: {verdict}\n")
        f.write(f"- risks: {json.dumps(risks, ensure_ascii=False)}\n")
        if notes:
            f.write(f"- notes: {notes}\n")
        f.write(f"- time: {_now_iso()}\n\n")


def run_evolution(generations: int, seed_path: str = None, task_id: str = None) -> str:
    """
    Runs the EoH evolutionary process for a specified number of generations (v3).
    Also updates tasks.json, project_truth.md, and evolution_ledger.jsonl.
    """
    sync_state()
    tasks = _read_json(TASKS_PATH)
    stage = tasks.get("currentStage", "evolve")
    tid = task_id or tasks.get("activeTaskId")
    if tid:
        update_task_status(tid, "doing")
    run_id = _new_run_id()

    default_seed_path = os.path.join(_V3_DIR, "refined_seeds.json")
    chosen_seed_path = seed_path or (default_seed_path if os.path.exists(default_seed_path) else None)

    try:
        result = _base.run_evolution(generations=generations, seed_path=chosen_seed_path)
        stats = _base.analyze_latest_results()
        run_error = None
    except Exception as e:
        result = f"Evolution failed: {e}"
        stats = {}
        run_error = str(e)

    output_base = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    trajectory_path = os.path.join(output_base, "results", "trajectory", "trajectory.jsonl")

    ledger = {
        "schemaVersion": "1.0",
        "runId": run_id,
        "time": _now_iso(),
        "stage": stage,
        "taskId": tid,
        "config": {
            "generations": generations,
            "seedPath": chosen_seed_path or "",
            "seedSource": "v3_agent/refined_seeds.json"
        },
        "artifacts": {
            "trajectoryPath": trajectory_path if os.path.exists(trajectory_path) else "",
            "bestCodePreview": (stats.get("best_code") or "")[:2000] if isinstance(stats, dict) else ""
        },
        "metrics": {
            "bestFitness": stats.get("best_fitness") if isinstance(stats, dict) else None,
            "noneRate": stats.get("none_rate") if isinstance(stats, dict) else None,
            "error": stats.get("last_error") if isinstance(stats, dict) else run_error
        },
        "errors": {
            "lastError": stats.get("last_error") if isinstance(stats, dict) else run_error,
            "lastTraceback": stats.get("last_traceback") if isinstance(stats, dict) else ""
        }
    }
    _append_evolution_ledger(ledger)

    append_project_truth_fact(
        summary=f"Evolution run completed for generations={generations}." if run_error is None else f"Evolution run failed for generations={generations}: {run_error}",
        stage=stage,
        task_id=tid,
        run_id=run_id,
        metrics={
            "bestFitness": stats.get("best_fitness") if isinstance(stats, dict) else None,
            "noneRate": stats.get("none_rate") if isinstance(stats, dict) else None
        },
        artifacts={"trajectoryPath": ledger["artifacts"]["trajectoryPath"]},
        decision="Review results and decide whether to refine PRM or continue evolution." if run_error is None else "Fix seed/config/runtime error then re-run evolution.",
        next_step="analyze_latest_results" if run_error is None else "sync_state"
    )

    if tid:
        update_task_status(tid, "done" if run_error is None else "blocked", notes=run_error or "")
    set_active_task(tasks.get("activeTaskId", tid) or "", stage=stage)
    return result


def run_code_review(code: str = None, task_id: str = None) -> str:
    """
    Runs reviewer gate (v3).
    Also appends to logs/review_log.md and updates tasks.json.
    """
    sync_state()
    tasks = _read_json(TASKS_PATH)
    tid = task_id or tasks.get("activeTaskId") or "VALIDATE-001"
    report = _base.run_code_review(code=code)
    verdict = "pass" if "PASS" in report else "fail"
    risks = []
    if verdict == "fail":
        risks.append("review_fail")
    _append_review_log(task_id=tid, verdict=verdict, risks=risks, notes="See report for details.")
    append_project_truth_fact(
        summary=f"Code review completed: {verdict}.",
        stage=tasks.get("currentStage"),
        task_id=tid,
        metrics=None,
        artifacts={"reviewLog": os.path.relpath(REVIEW_LOG_PATH, _V3_DIR)},
        decision="Proceed only if pass; otherwise refine or redesign PRM.",
        next_step="refine_best_code" if verdict == "fail" else "add_new_seed"
    )
    return report


analyze_latest_results = _base.analyze_latest_results
run_deep_analysis = _base.run_deep_analysis
design_new_prm = _base.design_new_prm
refine_best_code = _base.refine_best_code
update_research_notes = _base.update_research_notes
update_memory = _base.update_memory
update_plan = _base.update_plan
read_memory = _base.read_memory
read_plan = _base.read_plan
web_search = _base.web_search
fetch_paper_summary = _base.fetch_paper_summary
read_github_repo = _base.read_github_repo
read_research_notes = _base.read_research_notes
visualize_best_solution = _base.visualize_best_solution
generate_visual_report = _base.generate_visual_report
deploy_best_algorithm = _base.deploy_best_algorithm
run_comprehensive_evaluation = _base.run_comprehensive_evaluation
organize_research_notes = _base.organize_research_notes
update_handoff = _base.update_handoff
read_handoff = _base.read_handoff
add_new_seed = _base.add_new_seed
install_missing_package = _base.install_missing_package
