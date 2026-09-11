# agent-integration-skills

Two Claude Code skills for reviewing the architecture of agent systems and turning the review's
recommendations into testable decisions. Both were calibrated against `malston/agent-pipeline`
at commit `9af07b3`; the calibration fixtures live under each skill's `references/`.

| Skill | Does | Depends on |
| --- | --- | --- |
| `reviewing-agent-integration` | Reviews a codebase against the Agents Integration Patterns catalogue: intent, implementation, forces, one finding per pattern with a file-and-line citation, failure map, transport. Read-only. | ripgrep |
| `writing-pattern-selection-cards` | Consumes that review and writes a Pattern Selection Card for each mechanism change, plus a claim-corrections table for documentation fixes. A checker holds cards to the catalogue's invariants. | the review; the pattern files bundled in the first skill |

## Install

```bash
claudeup ext install skills ./reviewing-agent-integration
claudeup ext install skills ./writing-pattern-selection-cards
```

`claudeup ext install` copies; after editing here, reinstall (or remove and reinstall) to update
`~/.claudeup/ext/skills/`.

## Use

1. `Skill: reviewing-agent-integration` on a codebase. It runs `scripts/scan_patterns.py`, then
   writes a report in the shape of `references/report-template.md`.
2. `Skill: writing-pattern-selection-cards` on that report. It writes cards in the shape of
   `references/card-template.md` and runs `scripts/check_cards.py --repo <codebase>`.

Both scripts have `--help`.

## Calibration

Each skill's `references/calibration-agent-pipeline.md` records the expected output for the
agent-pipeline fixture and every run to date. After editing a skill or its script, regenerate and
diff against the fixture before trusting the change.

## Attribution

- `reviewing-agent-integration/references/patterns/`, `FORCES.md`, `FAILURE-MAP.md`, `TRANSPORT.md`:
  copied from `roanbrasil/agents-integration-patterns`, CC BY 4.0. License and source commit in that
  directory. Cross-links rewritten for the flat bundle; images and sample code not bundled.
- `writing-pattern-selection-cards/references/pattern-selection-card.md`, `six-step-methodology.md`,
  `pattern_selection_card_reference.py`: copied from `huangjia2019/agent-design-patterns`, MIT.
  License and source commit in that directory.

Everything else in this repository is by Mark Alston.
