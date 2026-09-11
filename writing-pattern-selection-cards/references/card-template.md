# Pattern Selection Cards: <codebase name>

Written <YYYY-MM-DD> from the review at `<review path>` (commit `<sha>`). Card definition follows
the Pattern Selection Card in _Designing AI Agents_ (Huang, MIT; source commit in
`references/SOURCE-COMMIT.txt`). Every card is a hypothesis in state `ready_for_trial`,
`blocked`, or `draft`; no card here is accepted, because acceptance needs a measured trial.

Evidence references use the review's tags or `file:line`. A precondition without a citation is an
error, not a note.

---

## Card <n>: <one-line title naming the recommendation>

Source finding: <pattern name>, status <status>, recommendation <verb>, at `<review path>:<line>`.

One paragraph for people: what the review found, what this card proposes, and what would make the
proposal wrong. No new claims here that are not in the JSON block below.

```json card
{
  "card_id": "psc-<codebase>-<nnn>",
  "version": 1,
  "source_finding": {
    "pattern": "<pattern id from the review>",
    "status": "<misapplied | absent, needed | present, adjust>",
    "recommendation": "<build | adopt | adjust | narrow the claim | remove the claim | remove>",
    "ref": "<review path>:<line>"
  },
  "problem": {
    "problem_id": "<short id>",
    "objective": "<what must be true when this is solved, one sentence>",
    "workload_ref": "<the representative workload the trial runs on: a test file, fixture, or dataset, cited>",
    "input_refs": ["<inputs the workload consumes, cited>"],
    "output_contract": "<what the system must produce, one sentence>",
    "dependency_shape": "<independent | ordered | shared_state>",
    "constraints": [
      "<hard constraints from the review's forces section, each naming its force>"
    ],
    "observed_baseline_failure": "<the failure the review observed, cited; empty string if none was observed>"
  },
  "baseline": {
    "candidate_id": "<id>",
    "patterns": [],
    "rationale": "<the smallest viable implementation: usually what the code does today, cited>"
  },
  "proposal": {
    "candidate_id": "<id>",
    "patterns": [
      {
        "name": "<pattern name>",
        "category": "<category from the catalogue>",
        "solves": "<the catalogue's Problem line, one sentence>",
        "preconditions": ["<key>", "..."]
      }
    ],
    "rationale": "<why this bundle answers the observed failure; names the force it buys and the force it spends>",
    "assumptions": [
      {
        "key": "<key matching a precondition>",
        "claim": "<what must be true>",
        "evidence_ref": "<file:line or [CODE ...]>"
      }
    ],
    "seams": [
      {
        "producer": "<pattern or component>",
        "consumer": "<pattern or component>",
        "artifact": "<what crosses>",
        "owner": "<who may change it>",
        "mutation_rule": "<read_only | replaceable_until_commit | append_only>",
        "version_field": "<field that versions it>"
      }
    ]
  },
  "rejected_alternatives": [
    {
      "candidate_id": "<id>",
      "reason": "<why not>",
      "evidence_ref": "<file:line, catalogue When-to-avoid, or review finding>"
    }
  ],
  "experiment": {
    "workload_ref": "<must equal problem.workload_ref>",
    "gates": [
      {
        "metric": "<name>",
        "comparison": "<at_least | at_most | equals>",
        "target": 0,
        "target_source": "<test or metric citation, or \"proposed\">"
      }
    ],
    "ablations": ["<multi-pattern candidates only: one removal per pattern and the loss it should show>"],
    "disconfirming_signals": [
      "<an observation that would show the hypothesis is wrong>"
    ],
    "rollback_plan": "<how to return to the baseline if the proposal fails>",
    "predicted_outcome": "<accepted | rejected>, because <one clause>; for a disjunctive recommendation, the rejection branch names the claim to remove"
  }
}
```

State after `scripts/check_cards.py`: <ready_for_trial | blocked | draft>. Findings, warnings
included: <list, or none>.

---

## Claim corrections

Findings whose fix is to a document, not a mechanism.

| Review finding | Document line | Code line it contradicts | Proposed wording |

## Cards not written

| Review finding | Why no card (one clause) |

## Sources

The review file and line ranges used. The catalogue files read. Codebase files read for evidence.

## Not verified

Workloads named but not run. Gates whose targets are proposed, not measured. Anything inferred.
