---
name: writing-pattern-selection-cards
description: Use when an architecture review of an agent system has produced recommendations and the next step is to turn each proposed pattern change into a falsifiable decision record with a baseline, preconditions, rejected alternatives, and an experiment plan, or when someone asks for a pattern selection card, an architecture decision card, or "how would we test whether this pattern is worth adding".
---

# Writing Pattern Selection Cards

## Overview

Turn a review's recommendations into Pattern Selection Cards as defined in _Designing AI Agents_
(Huang, MIT; bundled under `references/`). A card is a hypothesis with a smallest baseline, a
candidate, evidenced preconditions, rejected alternatives, and an experiment that alone may accept
or reject it. No card here is ever "accepted": acceptance needs a measured trial, and this skill
writes the plan for one.

Core rule: a card describes a change to a mechanism. A change to a document is not a card.

## When to use

- After `reviewing-agent-integration` or any review that names patterns to add, adjust, or remove.
- "Write a selection card for X", "how would we decide whether to add a dead-letter handler",
  "what experiment would justify this pattern".

Do not use before a review exists. The card's `source_finding` must cite one.

## Procedure

1. **Read the review.** List every finding with status misapplied, "absent, needed", or
   "present, adjust", with its recommendation verb and line number.

2. **Sort into cards and claim corrections.** Recommendation "build", "adopt", "adjust" (of a
   mechanism), or "remove" (of a mechanism) gets a card. Recommendation "narrow the claim" or
   "remove the claim", and any adjust whose change is to a design document only, goes to the
   claim-corrections table, one row: document line, code line that contradicts it, proposed
   wording. A finding whose recommendation is "land card N" is folded into card N as a second
   consumer, with its own seam row (one seam per consumer), not a card of its own. A disjunctive recommendation ("build X, or remove
   the claim") gets one card for the build branch; the remove-claim branch is recorded in that card's
   `experiment.predicted_outcome`, so the finding has one home.

3. **Bind the problem before naming the pattern.** For each card, fill `problem` first from the
   review's sections 1 to 3: objective, the representative workload, inputs, output contract,
   dependency shape, constraints (each naming its force), and the observed baseline failure. The
   workload must be a fixture, test, or dataset that exists, cited `file:line` or by path. If none
   exists, write `proposed://<name>` and describe it in prose; the checker will mark the card
   blocked, which is correct.

4. **Baseline is what the code does today.** Cite it. It is a candidate with no patterns.

5. **Candidate, preconditions, evidence.** Name the pattern and write `solves` as one sentence
   distilled from the catalogue's Problem section (the pattern files live in the
   `reviewing-agent-integration` skill under `references/patterns/`; if that skill is absent, use the
   review's `[CATALOGUE ...]` quotes). List preconditions as keys; every key gets an assumption with a claim and
   a citation. A precondition the codebase does not meet is still recorded, with the evidence that
   it is unmet; the card then predicts rejection, and says so.

6. **Seams and alternatives.** A multi-pattern candidate needs one seam contract per boundary.
   `version_field` is whatever a consumer checks to know the artifact changed (an attempt counter, a
   run id, a digest). At least one rejected alternative with the evidence for rejecting it; the
   catalogue's own When-to-avoid clause is admissible evidence when quoted.

7. **Experiment.** Same `workload_ref` as the problem. Each gate carries `target_source`: the test
   or metric the target came from, or `"proposed"`. Disconfirming signals and a rollback plan. For a
   multi-pattern candidate, one removal ablation per pattern.

8. **Check, then re-read every citation.** Run `python3 scripts/check_cards.py <file> --repo <repo>`
   so workload paths are checked for existence. Fix errors.
   Then open every `file:line` the cards cite and confirm the line says what the card says; line
   numbers drift and this is where cards go wrong. Record the checker's state per card in the prose.

## Card contract

The shape is `references/card-template.md`: a heading, one paragraph for people, a
` ```json card ` block for the checker, and the checker's state. Budget: 700 to 1,100 words per
card including the JSON, and one paragraph of prose per card; the range is wide because every
constraint, assumption, alternative, and gate carries a citation. A cards file for N mechanism findings
should land near 900N plus 400 for the tables; if it runs longer, the prose is repeating the JSON.

States: `ready_for_trial`; `blocked` (well formed, workload is `proposed://`); `draft` (any error).
A blocked card is often the right card to write; the prose says which fixture would unblock it. The
checker exits 0 unless a card is draft.

## Quick reference

| Situation                                      | Do                                                                   |
| ---------------------------------------------- | -------------------------------------------------------------------- |
| Recommendation is "remove the claim"           | Claim-corrections table, not a card                                  |
| Pattern is present, only its description wrong | Claim-corrections table                                              |
| No test exercises the failure | `proposed://` workload; card is blocked; say what fixture is needed |
| Gate target has no measured source             | `"target_source": "proposed"`; checker warns; say so in prose        |
| Precondition is unmet in this codebase         | Record it with evidence; predict rejection in prose                  |
| Two findings, one mechanism                    | One card; the second finding is a consumer on the seam               |
| Cited line does not say what the card says     | Fix the line number or drop the claim                                |

## Calibration

`references/calibration-agent-pipeline.md` records the expected card set for the agent-pipeline
review at commit `9af07b3`: which findings become cards, which become claim corrections, and the
expected checker state of each. After editing this skill or the checker, regenerate and diff.

## Common mistakes

- A card for a documentation fix. The schema has no branch for "pattern present, description
  wrong"; the corrections table does.
- Inventing a workload. A synthetic fixture that no test runs makes the experiment meaningless;
  name the missing fixture and let the card be blocked.
- Gate targets with no source. Every number in a gate came from somewhere or is marked proposed.
- Writing the JSON from the prose instead of the prose from the JSON. The block is the record; the
  paragraph explains it.
- Trusting line numbers from the review. Re-read them.

## Attribution

`references/pattern-selection-card.md`, `six-step-methodology.md`, and
`pattern_selection_card_reference.py` are copied from `huangjia2019/agent-design-patterns` (MIT;
license and source commit in `references/`). The checker reimplements that file's `review()`
invariants and adds citation, workload-availability, gate-source, and ablation checks.
