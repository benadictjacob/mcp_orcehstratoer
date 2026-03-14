"""
validation_suite.py
===================
Automated validation + sandbox testing for the MCP demo server.

PURPOSE:
    Every time a new capability is added to registry.json, run this
    to verify the new module is correctly wired, safe to call, and
    returns sensible output -- without touching the real system.

ARCHITECTURE:
    1. Registry Validator   -- checks registry.json integrity
    2. Module Validator     -- imports each module, checks run() exists
    3. Sandbox Executor     -- calls each capability with safe test inputs
    4. Output Interpreter   -- scores the output (non-empty, no crash, etc.)
    5. Change Detector      -- compares against last known good snapshot
    6. Report Generator     -- produces a human-readable validation report

HOW TO USE:
    As MCP capability:
        Input: "run"           -- validate everything
        Input: "run dashboard" -- validate only the dashboard module
        Input: "diff"          -- show what changed since last run
        Input: "report"        -- show last saved report
        Input: "snapshot"      -- save current state as new baseline
        Input: "sandbox dashboard start" -- call dashboard with 'start' in sandbox
"""

import json
import os
import sys
import importlib
import traceback
import time
from datetime import datetime

# Paths
BASE_DIR      = os.path.dirname(os.path.abspath(__file__))
REGISTRY_FILE = os.path.join(BASE_DIR, "registry.json")
SNAPSHOT_FILE = os.path.join(BASE_DIR, "validation_snapshot.json")
REPORT_FILE   = os.path.join(BASE_DIR, "validation_report.txt")

# Safe sandbox test inputs per capability -- chosen to be read-only / non-destructive
SANDBOX_INPUTS = {
    "add_numbers":            "5 3",
    "excel_login":            "test_user",
    "excel_read":             "nonexistent_test.xlsx",
    "excel_edit":             "invalid_session",
    "excel_list_sessions":    "",
    "create_excel_sample":    "test_output",
    "dynamic_executor":       "",
    "log_analyzer":           "",
    "analyze_logs":           "list",
    "files_list":             "",
    "files_read":             "nonexistent_test_file.txt",
    "files_delete":           "__SKIP__",
    "files_rename":           "__SKIP__",
    "files_copy":             "__SKIP__",
    "files_move":             "__SKIP__",
    "files_search":           "test_pattern_xyz_notexist",
    "files_large":            "9999",
    "c_drive":                "help",
    "c_drive_cleanup":        "help",
    "downloads_analyzer":     "help",
    "package_install":        "list",
    "canva":                  "check_auth",
    "quotes":                 "random",
    "weather":                "weather London",
    "crypto":                 "global",
    "countries":              "code US",
    "anime":                  "random",
    "webtools_base64_encode": "hello world",
    "webtools_base64_decode": "aGVsbG8gd29ybGQ=",
    "webtools_reverse":       "hello",
    "webtools_stats":         "hello world this is a test",
    "webtools_sort":          "banana\napple\ncherry",
    "webtools_find_replace":  "hello|world|goodbye",
    "webtools_password":      "16",
    "webtools_shuffle":       "one two three four",
    "webtools_case":          "upper hello world",
    "webtools_dedup":         "apple\nbanana\napple\ncherry",
    "webtools_url_encode":    "hello world",
    "webtools_json_beautify": '{"a":1,"b":2}',
    "webtools_json_minify":   '{"a": 1, "b": 2}',
    "webtools_list":          "",
    "llm":                    "health",
    "job_scraper":            "help",
    "dashboard":              "status",
}

REQUIRED_FIELDS = {"module", "function", "description"}


def load_registry():
    with open(REGISTRY_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def validate_registry(registry):
    issues = []
    for cap_name, cap_def in registry.items():
        missing = REQUIRED_FIELDS - set(cap_def.keys())
        if missing:
            issues.append("REGISTRY | {} | missing fields: {}".format(cap_name, missing))
        if not cap_def.get("description", "").strip():
            issues.append("REGISTRY | {} | description is empty".format(cap_name))
        if not cap_def.get("module", "").strip():
            issues.append("REGISTRY | {} | module is empty".format(cap_name))
        if not cap_def.get("function", "").strip():
            issues.append("REGISTRY | {} | function is empty".format(cap_name))
    return issues


def validate_module(cap_name, cap_def):
    result = {
        "capability":   cap_name,
        "module":       cap_def["module"],
        "function":     cap_def["function"],
        "import_ok":    False,
        "function_ok":  False,
        "error":        None,
    }
    try:
        if BASE_DIR not in sys.path:
            sys.path.insert(0, BASE_DIR)
        tools_dir = os.path.join(BASE_DIR, "tools")
        if os.path.isdir(tools_dir) and tools_dir not in sys.path:
            sys.path.insert(0, tools_dir)

        mod = importlib.import_module(cap_def["module"])
        result["import_ok"] = True
        func = getattr(mod, cap_def["function"], None)
        if func and callable(func):
            result["function_ok"] = True
        else:
            result["error"] = "function '{}' not found or not callable".format(cap_def["function"])
    except Exception as e:
        result["error"] = str(e)
    return result


def sandbox_run(cap_name, cap_def, test_input=None):
    result = {
        "capability":  cap_name,
        "test_input":  test_input,
        "status":      "SKIP",
        "output":      "",
        "output_len":  0,
        "duration_ms": 0,
        "error":       None,
    }

    if test_input == "__SKIP__":
        result["status"] = "SKIPPED"
        result["output"] = "Destructive operation -- skipped for safety"
        return result

    try:
        mod  = importlib.import_module(cap_def["module"])
        func = getattr(mod, cap_def["function"])

        t0  = time.time()
        out = func(test_input) if test_input is not None else func()
        elapsed = int((time.time() - t0) * 1000)

        out_str = str(out) if out is not None else ""
        result["status"]      = "PASS" if out_str.strip() else "WARN_EMPTY"
        result["output"]      = out_str[:400]
        result["output_len"]  = len(out_str)
        result["duration_ms"] = elapsed

    except Exception as e:
        result["status"] = "FAIL"
        result["error"]  = traceback.format_exc(limit=4)

    return result


def interpret_result(r):
    s = r["status"]
    if s == "SKIPPED":
        return "SKIPPED (destructive op)"
    if s == "FAIL":
        err = (r["error"] or "")[:120].replace("\n", " ")
        return "FAIL -- {}".format(err)
    if s == "WARN_EMPTY":
        return "WARN -- returned empty string"
    if s == "PASS":
        return "PASS -- {} chars in {}ms".format(r["output_len"], r["duration_ms"])
    return s


def load_snapshot():
    if not os.path.exists(SNAPSHOT_FILE):
        return {}
    with open(SNAPSHOT_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_snapshot(data):
    with open(SNAPSHOT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def detect_changes(current_registry, snapshot):
    added   = [k for k in current_registry if k not in snapshot]
    removed = [k for k in snapshot if k not in current_registry]
    changed = []
    for k in current_registry:
        if k in snapshot and current_registry[k] != snapshot.get(k, {}).get("definition"):
            changed.append(k)
    return added, removed, changed


def build_report(reg_issues, mod_results, sandbox_results, added, removed, changed):
    lines = []
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines.append("=" * 70)
    lines.append("  MCP DEMO SERVER -- VALIDATION REPORT")
    lines.append("  Generated: {}".format(ts))
    lines.append("=" * 70)

    lines.append("")
    lines.append("CHANGE DETECTION vs last snapshot")
    lines.append("-" * 40)
    if not added and not removed and not changed:
        lines.append("  No changes detected.")
    if added:
        lines.append("  NEW capabilities ({})".format(len(added)))
        for a in added:
            lines.append("    + {}".format(a))
    if removed:
        lines.append("  REMOVED capabilities ({})".format(len(removed)))
        for r in removed:
            lines.append("    - {}".format(r))
    if changed:
        lines.append("  MODIFIED capabilities ({})".format(len(changed)))
        for c in changed:
            lines.append("    ~ {}".format(c))

    lines.append("")
    lines.append("REGISTRY VALIDATION")
    lines.append("-" * 40)
    if not reg_issues:
        lines.append("  All {} registry entries are well-formed. OK".format(
            len(mod_results)))
    else:
        for issue in reg_issues:
            lines.append("  ISSUE: {}".format(issue))

    lines.append("")
    lines.append("MODULE IMPORT CHECKS")
    lines.append("-" * 40)
    import_fails = [r for r in mod_results if not r["import_ok"] or not r["function_ok"]]
    if not import_fails:
        lines.append("  All {} modules imported successfully. OK".format(len(mod_results)))
    else:
        for r in import_fails:
            lines.append("  FAIL | {} | {}".format(r["capability"], r["error"]))

    lines.append("")
    lines.append("SANDBOX EXECUTION RESULTS")
    lines.append("-" * 40)
    pass_count = sum(1 for r in sandbox_results if r["status"] == "PASS")
    fail_count = sum(1 for r in sandbox_results if r["status"] == "FAIL")
    warn_count = sum(1 for r in sandbox_results if r["status"] == "WARN_EMPTY")
    skip_count = sum(1 for r in sandbox_results if r["status"] in ("SKIP","SKIPPED"))
    lines.append("  PASS: {}  FAIL: {}  WARN: {}  SKIP: {}".format(
        pass_count, fail_count, warn_count, skip_count))
    lines.append("")

    for r in sandbox_results:
        verdict = interpret_result(r)
        lines.append("  [{:10s}] {:35s} {}".format(r["status"], r["capability"], verdict))

    lines.append("")
    lines.append("RECOMMENDATIONS")
    lines.append("-" * 40)
    recs = []
    if added:
        recs.append("New capabilities added -- add sandbox test inputs for: {}".format(
            ", ".join(added)))
    if fail_count > 0:
        failed = [r["capability"] for r in sandbox_results if r["status"] == "FAIL"]
        recs.append("Fix failing modules: {}".format(", ".join(failed)))
    if import_fails:
        recs.append("Fix import errors: {}".format(
            ", ".join(r["capability"] for r in import_fails)))
    if reg_issues:
        recs.append("Fix registry issues listed above.")
    if not recs:
        recs.append("All checks passed. Safe to proceed.")
    for rec in recs:
        lines.append("  * {}".format(rec))

    lines.append("")
    lines.append("=" * 70)
    return "\n".join(lines)


def run_validation(target=None):
    registry = load_registry()

    if target:
        if target not in registry:
            return "Unknown capability: '{}'. Available: {}".format(
                target, ", ".join(registry.keys()))
        registry = {target: registry[target]}

    reg_issues   = validate_registry(registry)
    mod_results  = [validate_module(name, defn) for name, defn in registry.items()]

    sandbox_results = []
    full_reg = load_registry()
    for mod_res in mod_results:
        cap  = mod_res["capability"]
        defn = full_reg[cap]
        if mod_res["import_ok"] and mod_res["function_ok"]:
            test_in = SANDBOX_INPUTS.get(cap, "")
            sb = sandbox_run(cap, defn, test_in)
        else:
            sb = {"capability": cap, "status": "FAIL", "output": "",
                  "output_len": 0, "duration_ms": 0,
                  "error": mod_res["error"], "test_input": None}
        sandbox_results.append(sb)

    full_registry = load_registry()
    snapshot = load_snapshot()
    snap_defs = {k: v.get("definition") for k, v in snapshot.items()}
    added, removed, changed = detect_changes(full_registry, snap_defs)

    report = build_report(reg_issues, mod_results, sandbox_results, added, removed, changed)

    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        f.write(report)

    return report


def run(input_str=""):
    parts = input_str.strip().split(maxsplit=1) if input_str.strip() else ["run"]
    cmd   = parts[0].lower()
    arg   = parts[1].strip() if len(parts) > 1 else ""

    if cmd in ("run", "validate", "check", "all", ""):
        return run_validation(arg if arg else None)

    elif cmd == "sandbox":
        if not arg:
            return "Usage: sandbox <capability_name> [input]\nExample: sandbox dashboard status"
        sub      = arg.split(maxsplit=1)
        cap_name = sub[0]
        custom_in = sub[1] if len(sub) > 1 else SANDBOX_INPUTS.get(cap_name, "")
        registry = load_registry()
        if cap_name not in registry:
            return "Unknown capability: {}".format(cap_name)
        defn = registry[cap_name]
        mr = validate_module(cap_name, defn)
        if not mr["import_ok"]:
            return "Cannot import module '{}': {}".format(defn["module"], mr["error"])
        result = sandbox_run(cap_name, defn, custom_in)
        lines = [
            "SANDBOX TEST: {}".format(cap_name),
            "Input   : {}".format(repr(custom_in)),
            "Status  : {}".format(result["status"]),
            "Duration: {}ms".format(result["duration_ms"]),
            "Output  :",
            result["output"] if result["output"] else "(empty)",
        ]
        if result.get("error"):
            lines.append("Error:")
            lines.append(result["error"])
        return "\n".join(lines)

    elif cmd == "diff":
        registry  = load_registry()
        snapshot  = load_snapshot()
        snap_defs = {k: v.get("definition") for k, v in snapshot.items()}
        added, removed, changed = detect_changes(registry, snap_defs)
        lines = ["CHANGE DIFF vs last snapshot ('snapshot' command to update baseline)"]
        if not added and not removed and not changed:
            lines.append("  No changes.")
        lines += ["  + NEW: {}".format(a) for a in added]
        lines += ["  - REMOVED: {}".format(r) for r in removed]
        lines += ["  ~ CHANGED: {}".format(c) for c in changed]
        return "\n".join(lines)

    elif cmd == "snapshot":
        registry = load_registry()
        snap = {k: {"definition": v, "snapshotted_at": datetime.now().isoformat()}
                for k, v in registry.items()}
        save_snapshot(snap)
        return "Snapshot saved. {} capabilities recorded as baseline.".format(len(registry))

    elif cmd == "report":
        if not os.path.exists(REPORT_FILE):
            return "No report found. Run 'run' first."
        with open(REPORT_FILE, "r", encoding="utf-8") as f:
            return f.read()

    elif cmd == "list":
        registry = load_registry()
        lines = ["Registered capabilities ({} total):".format(len(registry))]
        for name, defn in registry.items():
            has_sandbox = name in SANDBOX_INPUTS
            lines.append("  {:35s} module={:25s} sandbox={}".format(
                name, defn["module"], "YES" if has_sandbox else "NO"))
        return "\n".join(lines)

    else:
        return (
            "Validation Suite Commands:\n"
            "  run [capability]       -- Run full validation (or one capability)\n"
            "  sandbox <cap> [input]  -- Execute a capability safely in sandbox\n"
            "  diff                   -- Show changes vs last snapshot\n"
            "  snapshot               -- Save current registry as baseline\n"
            "  report                 -- Show last saved validation report\n"
            "  list                   -- List all capabilities and sandbox status\n\n"
            "Examples:\n"
            "  run\n"
            "  run dashboard\n"
            "  sandbox crypto global\n"
            "  sandbox weather weather Tokyo\n"
            "  diff\n"
            "  snapshot"
        )
