# Calibration fixture: agent-pipeline cards

Expected card set for the `reviewing-agent-integration` review of `~/code/agent-pipeline` at commit
`9af07b3` (review file: the fourth calibration run, 2026-09-10). Use: regenerate the cards from that
review and diff against this list. Update only when a difference is shown to be a fixture error, and
say why in the commit.

## Baseline without the skill (2026-09-10)

Eight prose cards, 6,330 words, no machine-checkable structure. Five of the eight were documentation
fixes forced into the card schema. Workloads and gate targets were invented and self-flagged. Three
citations wrong on first pass.

## Expected with the skill

Cards (mechanism changes):

| card | source finding | expected state |
| --- | --- | --- |
| dead-letter-agent, adopt; reflection-loop folded in as seam consumer | review l.206, l.279 | ready_for_trial (workload `tests/test_reflection.py` exhaustion tests; gate targets may be proposed) |
| llm-as-judge, adjust (judge model seam) | review l.258 | blocked (no test drives the LLM judge path; workload proposed://) |
| exception-handler-chain, build; predicts rejection, remove-claim branch as rejection outcome | review l.234 | blocked (no test drives re-prompt; workload proposed://) |

Claim corrections (document fixes, not cards): checkpoint-resume (`DESIGN.md:85-86`,
`tests/test_graph.py:5`); tool-provider (`DESIGN.md:36`, `DESIGN.md:241-243`);
least-privilege-tool-scope (`DESIGN.md:256-261`); context-injection (`DESIGN.md:304-312`,
`DESIGN.md:120-121`).

Cards not written: reflection-loop (folded), tool-provider shared executor (suggestion, not a
recommendation), every "leave".

Checker final line expected: `1 ready_for_trial, 2 blocked, 0 draft of 3 cards`, exit 0.
Word count expected: 2,400 to 3,700.

## Runs

- 2026-09-10 first skill run (fixture unseen): 3 cards, 4 corrections, 2,931 words, checker
  `1/3 ready` under the old two-state checker; the two blocked cards were then reported as draft.
  Nine defects in skill, template, and checker reported and fixed the same day.
- 2026-09-10 second skill run (installed, fixture unseen): 3 cards in the expected states, 7
  correction rows over the 4 expected findings (one row per document line), 3,631 words, checker
  `1 ready_for_trial, 2 blocked, 0 draft`, exit 0. Eight wording and checker defects reported and
  fixed the same day; those fixes have not yet been run against this fixture.
