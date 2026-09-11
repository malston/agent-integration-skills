# Example card (validator fixture)

Adapted from the catalogue's `example.py`. Passes `check_cards.py` as `ready_for_trial`.

```json card
{
  "card_id": "psc-example-001",
  "version": 1,
  "source_finding": {
    "pattern": "fan-out-gather",
    "status": "absent, needed",
    "recommendation": "adopt",
    "ref": "review.md:120"
  },
  "problem": {
    "problem_id": "june-reconciliation",
    "objective": "locate the payroll discrepancy",
    "workload_ref": "fixture://payroll/june/v1",
    "input_refs": ["snapshot://payroll", "snapshot://ledger"],
    "output_contract": "evidenced discrepancy report",
    "dependency_shape": "independent",
    "constraints": ["read-only (F5 blast radius)"],
    "observed_baseline_failure": "single-source check missed one disagreement (fixture://payroll/june/v1 run 3)"
  },
  "baseline": {
    "candidate_id": "single-source",
    "patterns": [],
    "rationale": "smallest viable read-only check"
  },
  "proposal": {
    "candidate_id": "fanout",
    "patterns": [
      {
        "name": "Fan-out and Gather",
        "category": "collaboration",
        "solves": "compare independent source readings",
        "preconditions": ["independent_sources"]
      }
    ],
    "rationale": "the source snapshots are independently owned; buys F4 reliability, spends F1 latency",
    "assumptions": [
      {
        "key": "independent_sources",
        "claim": "each source owns a separate snapshot",
        "evidence_ref": "schema://source-lineage/v1"
      }
    ],
    "seams": []
  },
  "rejected_alternatives": [
    {
      "candidate_id": "iterative-hypothesis",
      "reason": "one source result does not change the next source query",
      "evidence_ref": "fixture://payroll/june/dependency-map"
    }
  ],
  "experiment": {
    "workload_ref": "fixture://payroll/june/v1",
    "gates": [
      { "metric": "defect_recall", "comparison": "at_least", "target": 1.0, "target_source": "fixture://payroll/june/v1#defect-list" },
      { "metric": "false_consensus", "comparison": "at_most", "target": 0.0, "target_source": "proposed" }
    ],
    "disconfirming_signals": ["sources share an upstream baseline"],
    "rollback_plan": "retain the single-source check"
  }
}
```

A second block that must come out `draft` (precondition unevidenced, no rejected alternative,
workload mismatch):

```json card
{
  "card_id": "psc-example-bad",
  "version": 1,
  "source_finding": {
    "pattern": "x",
    "status": "absent, needed",
    "recommendation": "adopt",
    "ref": "no citation"
  },
  "problem": {
    "problem_id": "p",
    "objective": "o",
    "workload_ref": "fixture://a",
    "input_refs": ["i"],
    "output_contract": "c",
    "dependency_shape": "ordered",
    "constraints": ["k"],
    "observed_baseline_failure": ""
  },
  "baseline": { "candidate_id": "b", "patterns": [], "rationale": "r" },
  "proposal": {
    "candidate_id": "p",
    "patterns": [
      { "name": "A", "category": "c", "solves": "s", "preconditions": ["pre"] },
      { "name": "B", "category": "c", "solves": "s" }
    ],
    "rationale": "r",
    "assumptions": [{ "key": "pre", "claim": "c", "evidence_ref": "trust me" }],
    "seams": []
  },
  "rejected_alternatives": [],
  "experiment": {
    "workload_ref": "fixture://b",
    "gates": [{ "metric": "m", "comparison": "at_least", "target": 1 }],
    "disconfirming_signals": ["d"],
    "rollback_plan": "r"
  }
}
```
