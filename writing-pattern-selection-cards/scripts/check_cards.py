#!/usr/bin/env python3
"""Check Pattern Selection Cards for the invariants the catalogue's reference enforces.

Why: a card is an architecture hypothesis. The catalogue's reference implementation refuses
to call a card ready until every pattern precondition is claimed and evidenced, a
multi-pattern candidate has a seam contract, at least one alternative was rejected with
evidence, and the experiment runs on the same workload the problem was bound to. A card
written in prose drifts from those rules; this script holds it to them.

When: run on every cards file before handing it over, and again after edits.

Usage:
  check_cards.py <cards.md> [--repo <codebase>] [--json out.json] [--help]

Input: a markdown file with one or more fenced blocks tagged ```json card``` (one card
each; the surrounding prose is for people). Card schema: see references/card-template.md.
Output: one block per card with its state and findings. States: ready_for_trial (no
errors, workload exists), blocked (well formed, but the workload is proposed://), draft
(errors). Exit 0 if no card is draft, 1 if any card is draft, 2 on bad input. A blocked card
is a correct card whose trial cannot run yet; it does not fail the check.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

FENCE = re.compile(r"```json\s+card\s*\n(.*?)\n```", re.S)
EVIDENCE = re.compile(r"(^[\w./-]+:\d+(-\d+)?(,\s*\d+(-\d+)?)*$)|(^[a-z][a-z0-9+.-]*://)|(^\[(CODE|DOC|SCAN|CATALOGUE)\b[^\]]*[\w./-]+:\d+)|(^\[CATALOGUE\b[^\]]*§)")

REQUIRED_PROBLEM = ("problem_id", "objective", "workload_ref", "input_refs", "output_contract",
                    "dependency_shape", "constraints")  # observed_baseline_failure may be empty: warning only
REQUIRED_CANDIDATE = ("candidate_id", "patterns", "rationale")
REQUIRED_PATTERN = ("name", "category", "solves")
REQUIRED_SEAM = ("producer", "consumer", "artifact", "owner", "mutation_rule", "version_field")
REQUIRED_EXPERIMENT = ("workload_ref", "gates", "disconfirming_signals", "rollback_plan")
DEPENDENCY_SHAPES = {"independent", "ordered", "shared_state"}
COMPARISONS = {"at_least", "at_most", "equals"}


def err(findings: list, code: str, detail: str) -> None:
    findings.append({"severity": "error", "code": code, "detail": detail})


def warn(findings: list, code: str, detail: str) -> None:
    findings.append({"severity": "warning", "code": code, "detail": detail})


def missing(obj: dict, keys: tuple, where: str, findings: list) -> None:
    for k in keys:
        v = obj.get(k)
        if v is None or (isinstance(v, (str, list)) and not v):
            err(findings, "missing_field", f"{where}.{k} is required")


def looks_like_evidence(ref: str) -> bool:
    return bool(ref) and bool(EVIDENCE.search(ref.strip()))


def check_card(card: dict, repo: Path | None = None) -> tuple[str, list]:
    f: list = []
    for k in ("card_id", "version", "source_finding", "problem", "baseline", "proposal",
              "rejected_alternatives", "experiment"):
        if k not in card:
            err(f, "missing_field", f"card.{k} is required")
    if f:
        return "draft", f

    if not isinstance(card["version"], int) or card["version"] < 1:
        err(f, "bad_version", "version must be an integer >= 1")

    p = card["problem"]
    missing(p, REQUIRED_PROBLEM, "problem", f)
    if "observed_baseline_failure" not in p:
        err(f, "missing_field", "problem.observed_baseline_failure is required (may be an empty string)")
    if p.get("dependency_shape") not in DEPENDENCY_SHAPES:
        err(f, "bad_dependency_shape", f"problem.dependency_shape must be one of {sorted(DEPENDENCY_SHAPES)}")
    if not str(p.get("observed_baseline_failure", "")).strip():
        warn(f, "baseline_failure_not_observed",
             "No measured baseline failure explains why more architecture is needed.")

    for role in ("baseline", "proposal"):
        c = card[role]
        missing(c, REQUIRED_CANDIDATE, role, f) if role == "proposal" else missing(
            c, ("candidate_id", "rationale"), role, f)
        for i, pat in enumerate(c.get("patterns", [])):
            missing(pat, REQUIRED_PATTERN, f"{role}.patterns[{i}]", f)
    if card["baseline"].get("candidate_id") == card["proposal"].get("candidate_id"):
        err(f, "baseline_equals_proposal", "baseline and proposal must be distinct candidates")

    prop = card["proposal"]
    assumptions = {a.get("key"): a for a in prop.get("assumptions", [])}
    for pat in prop.get("patterns", []):
        for pre in pat.get("preconditions", []):
            a = assumptions.get(pre)
            if a is None:
                err(f, "precondition_not_claimed",
                    f"{pat.get('name')} requires {pre!r}, but the card does not claim it.")
            elif not looks_like_evidence(str(a.get("evidence_ref", ""))):
                err(f, "precondition_not_evidenced",
                    f"{pat.get('name')} requires {pre!r}; evidence_ref is missing or not a citation "
                    f"(file:line, [CODE ...], or scheme://).")
    if len(prop.get("patterns", [])) > 1 and not prop.get("seams"):
        err(f, "missing_seam_contract", "A multi-pattern candidate must define at least one seam contract.")
    for i, seam in enumerate(prop.get("seams", [])):
        missing(seam, REQUIRED_SEAM, f"proposal.seams[{i}]", f)

    alts = card["rejected_alternatives"]
    if not alts:
        err(f, "alternative_not_considered",
            "Name at least one rejected alternative and the evidence for rejecting it.")
    for i, alt in enumerate(alts):
        missing(alt, ("candidate_id", "reason", "evidence_ref"), f"rejected_alternatives[{i}]", f)
        if alt.get("evidence_ref") and not looks_like_evidence(str(alt["evidence_ref"])):
            err(f, "alternative_not_evidenced",
                f"rejected_alternatives[{i}].evidence_ref is not a citation")

    e = card["experiment"]
    missing(e, REQUIRED_EXPERIMENT, "experiment", f)
    wl = str(p.get("workload_ref", ""))
    if wl.startswith("proposed://"):
        f.append({"severity": "blocked", "code": "workload_not_available",
                  "detail": "problem.workload_ref is proposed://; the card is blocked until the fixture exists."})
    elif not looks_like_evidence(wl) and "://" not in wl and not re.match(r"^[\w./-]+$", wl):
        err(f, "workload_not_cited", "problem.workload_ref must be a path, file:line, or scheme:// reference")
    elif repo is not None and "://" not in wl:
        rel = wl.split(":")[0].split(",")[0].strip()
        if not (repo / rel).exists():
            err(f, "workload_missing", f"problem.workload_ref path {rel!r} does not exist under {repo}")
    if len(prop.get("patterns", [])) > 1 and not e.get("ablations"):
        warn(f, "ablation_missing",
             "A multi-pattern candidate should name one removal ablation per pattern (experiment.ablations).")
    if e.get("workload_ref") != p.get("workload_ref"):
        err(f, "workload_binding_mismatch",
            "The experiment must use the workload bound into the problem contract.")
    for i, g in enumerate(e.get("gates", [])):
        missing(g, ("metric", "comparison", "target"), f"experiment.gates[{i}]", f)
        if g.get("comparison") not in COMPARISONS:
            err(f, "bad_comparison", f"experiment.gates[{i}].comparison must be one of {sorted(COMPARISONS)}")
        if not isinstance(g.get("target"), (int, float)):
            err(f, "bad_target", f"experiment.gates[{i}].target must be a number")
        src = str(g.get("target_source", "")).strip()
        if not src:
            err(f, "target_source_missing",
                f"experiment.gates[{i}].target_source is required: a test or metric citation, or \"proposed\"")
        elif src == "proposed":
            warn(f, "target_proposed", f"experiment.gates[{i}] target {g.get('target')} is proposed, not measured")
        elif not looks_like_evidence(src):
            err(f, "target_source_not_cited",
                f"experiment.gates[{i}].target_source must be a citation (file:line, [CODE ...], scheme://) or \"proposed\"")

    sf = card.get("source_finding", {})
    if not looks_like_evidence(str(sf.get("ref", ""))):
        err(f, "source_finding_not_cited",
            "source_finding.ref must point at the review finding (file:line or [CODE ...]).")

    if any(x["severity"] == "error" for x in f):
        state = "draft"
    elif any(x["severity"] == "blocked" for x in f):
        state = "blocked"
    else:
        state = "ready_for_trial"
    return state, f


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cards", help="markdown file containing ```json card``` blocks")
    ap.add_argument("--json", dest="json_out", help="write results to this file")
    ap.add_argument("--repo", help="codebase root; when given, non-proposed workload paths must exist")
    args = ap.parse_args()
    path = Path(args.cards).expanduser()
    if not path.is_file():
        print(f"error: {path} is not a file", file=sys.stderr)
        return 2
    blocks = FENCE.findall(path.read_text())
    if not blocks:
        print("error: no ```json card``` blocks found", file=sys.stderr)
        return 2

    results = []
    any_draft = False
    for i, raw in enumerate(blocks, 1):
        try:
            card = json.loads(raw)
        except json.JSONDecodeError as exc:
            print(f"card {i}: invalid JSON: {exc}")
            any_draft = True
            results.append({"index": i, "state": "draft", "findings": [{"severity": "error", "code": "invalid_json", "detail": str(exc)}]})
            continue
        state, findings = check_card(card, Path(args.repo).expanduser() if args.repo else None)
        any_draft |= state == "draft"
        cid = card.get("card_id", f"card {i}")
        print(f"{cid}: {state}")
        for x in findings:
            print(f"  [{x['severity']}] {x['code']}: {x['detail']}")
        results.append({"index": i, "card_id": cid, "state": state, "findings": findings})

    ready = sum(1 for r in results if r["state"] == "ready_for_trial")
    blocked = sum(1 for r in results if r["state"] == "blocked")
    drafts = sum(1 for r in results if r["state"] == "draft")
    print(f"\n{ready} ready_for_trial, {blocked} blocked, {drafts} draft of {len(results)} cards")
    if args.json_out:
        Path(args.json_out).write_text(json.dumps(results, indent=2))
    return 1 if any_draft else 0


if __name__ == "__main__":
    sys.exit(main())
