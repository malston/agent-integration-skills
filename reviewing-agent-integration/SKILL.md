---
name: reviewing-agent-integration
description: Use when asked to review, audit, or assess the architecture of a codebase that connects AI agents to tools, models, or each other (LangGraph, MCP, A2A, multi-agent, orchestrator, pipeline, supervisor), or when asked which integration patterns a codebase uses, misuses, or lacks, or whether its design matches its implementation.
---

# Reviewing Agent Integration

## Overview

Review a codebase against the Agents Integration Patterns catalogue (Hohpe and Woolf lineage,
CC BY 4.0, bundled under `references/`). The output is a report with a fixed shape: intent first,
implementation second, forces third, then one finding per pattern with a file-and-line citation
behind every verdict. Read-only. No finding without evidence.

Core rule: a scanner hit is a candidate, not a verdict. A retry loop is not a circuit breaker.

## When to use

- "Review the architecture of this agent system", "which patterns does this use", "does the code
  match the design doc", "is this over-engineered for what it does".
- Any codebase with agents, tools, MCP servers, LangGraph graphs, A2A endpoints, or brokers.

Do not use for single-model prompt-and-response apps with no tools or agents: run step 1 and stop
with a one-paragraph "not an integration problem" note.

## Procedure

1. **Scan.** `python3 scripts/scan_patterns.py <repo> --json <out>.json`. Read the topology block
   first. Hits are split into code, doc, and config. A pattern with doc hits and no code hits is
   stated intent. Docstring prose counts as code; check it with `--show <id>` before confirming. `--show` prints
   one line per hit, indented two spaces, as `[kind] path:line: text`, where kind is code, doc, or
   config; filter with a pattern that does not anchor at line start.

2. **Intent.** Read README and the design documents the scanner's doc hits point at. Write report
   section 1: what the codebase says it is, which rung of the complexity ladder it claims (direct
   model call, single agent with tools, several agents), which topology. Cite `[DOC file:line]`.

3. **Implementation.** Write section 2 from code alone: the rung and topology the code implements.
   Every disagreement with section 1 is one sentence here and one finding later. Cite
   `[CODE file:line]` with paths relative to the repo root, never abbreviated.

4. **Forces.** Read `references/FORCES.md`. Write section 3: which of F1 to F14 this codebase's
   context weights, with the evidence, and which it does not. This section comes before any verdict
   so verdicts can refer to it.

5. **Select patterns.** A pattern gets a finding if any of these hold: it has a confirmed code hit;
   it has a doc hit that states intent; or it appears in the Related Patterns or Participants of a
   pattern with status misapplied, present-adjust, or present-fitting, whatever the relation verb (`uses`, `complements`, `used-by`, or none),
   and it passes at least one of the three "needed" tests in the status table. A companion that
   passes none is "absent, not needed" and goes to section 7 as one line, not a finding.
   Every other pattern, and every scanner candidate you reject, gets one line in section 7.

6. **Write findings.** Read `references/patterns/<id>.md` for each selected pattern. Assign one
   status from the vocabulary below. Take the heading's category and maturity from `references/matrix.md`.
   If the file has a `When to avoid` or `When to Avoid` section, quote the clause that applies or
   say none does; if it has no such section, write "no when-to-avoid clause in the catalogue".

7. **Failure map and transport.** From `references/FAILURE-MAP.md`, list only the modes this
   topology can exhibit (omit the others), and which present pattern covers each or that it is open. From
   `references/TRANSPORT.md`, note only warnings that apply to the transports the scanner found.

8. **Write and check.** Fill `references/report-template.md`. Then verify: every status has a
   citation; every build, adopt, or adjust recommendation names the force it buys and the force it spends
   (a documentation-only change spends none; say so);
   each section 1 versus 2 disagreement has a finding; section 7 rows are one line; the scan JSON
   path is in the header; word count is inside the budget below.

## Status vocabulary

| Status             | Meaning                                                                    | Length   |
| ------------------ | -------------------------------------------------------------------------- | -------- |
| misapplied | The code carries the pattern's name or any part of its mechanism, and departs from the Solution section (a mechanism half built is misapplied, not absent) | full |
| absent, needed | Not in code, and one of: a design document claims it; the failure map leaves open a mode this topology can exhibit, this pattern is a full (✅) mitigator of it, and the pattern file's Context section describes this codebase; section 3 weights a force only it resolves. One open mode makes at most one absent pattern needed: the ✅ mitigator whose Context fits, then highest maturity, then the one already named by a present pattern's Related Patterns | full |
| present, adjust    | In code and fitting, with a named departure worth fixing                   | full     |
| present, fitting   | In code, matches Solution, no departure                                    | short    |
| absent, not needed | A companion not present that meets none of the three "needed" tests | one line, section 7 |
| not applicable     | Nothing in code or docs calls for it                                       | one line |

Full is about 250 words. Short is under 120: status, evidence, one sentence of fit, the
when-to-avoid clause or "no when-to-avoid clause in the catalogue", recommendation "leave". For "absent, not needed", the recommendation is "leave until <condition>", taking the condition
from the when-to-avoid clause when the file has one and from section 3 otherwise. When a design
document claims a pattern, the status is "absent, needed" if the code has none of the pattern's
mechanism and "misapplied" if it has any part of it; the recommendation is "build" or "remove
the claim" or "narrow the claim". The design-versus-code disagreement is the finding.

Findings order: misapplied; absent, needed; present, adjust; present, fitting. Section 7 then
holds, one line each: absent-not-needed companions with their "leave until" condition, rejected
scanner candidates with the reason, and not-applicable patterns (these last may share a line when
the reason is the same).

## Report contract

The template in `references/report-template.md` is the deliverable's shape. Evidence tags:
`[CODE file:line]`, `[DOC file:line]`, `[SCAN n/m/k]` (code, doc, config hits), `[CATALOGUE
pattern §section]`, `[JUDGMENT]`. The finding heading carries the catalogue's category and maturity
from `references/matrix.md`; this catalogue has no topology axis.

Budget: 3,000 to 4,500 words for a codebase under 5,000 source lines; add 500 words for each
further 10,000 lines, to a ceiling of 6,500. The scanner's header reports the line count for code
files only (notebooks, vendored and static assets, docs, and config excluded); use that number. Count words with `wc -w` on the whole file, tags and
paths included. If the count exceeds the budget, the fix is shortening "present, fitting" findings and moving "absent, not
needed" companions to section 7, never dropping citations.

## Quick reference

| Situation                            | Do                                                                                          |
| ------------------------------------ | ------------------------------------------------------------------------------------------- |
| Doc hit, no code hit                 | "absent, needed" or "absent, not needed"; note "stated intent"                              |
| Code hit, Solution differs           | "misapplied"; name the departure with `[CODE]`                                              |
| Scanner hit is not the pattern       | One line in section 7 with the reason (e.g. `model.invoke` is not agent-to-agent messaging) |
| Scanner missed a hand-rolled version | Add it with `[CODE]`; list the miss under Not verified                                      |
| Verdict without a citation           | Delete the verdict or find the line                                                         |

## Calibration

`references/calibration-agent-pipeline.md` holds expected verdicts for `~/code/agent-pipeline`
at commit `9af07b3`. After editing this skill or the scanner, review that repo and diff the verdict
column. A changed verdict is either a skill regression or a fixture correction; decide which and
record it in the fixture.

## Common mistakes

- Verdicts before the forces profile; section 3 exists so each verdict names the force this
  codebase weights.
- Treating a design document's present tense as implementation. Section 2 is written from code.
- Judging fit against the catalogue's generic force list instead of section 3.
- Full findings for "present, fitting" patterns. That is how a review reaches 6,000 words.
- Path abbreviations. Cite the full relative path every time.
- Skipping the scanner and reading the whole repository. The scan is what makes the code-versus-doc
  split visible and keeps the review inside budget.

## Attribution

Pattern documents under `references/patterns/`, `FORCES.md`, `FAILURE-MAP.md`, and `TRANSPORT.md`
are copied from `roanbrasil/agents-integration-patterns` (CC BY 4.0; license and source commit in
`references/`). Cross-links inside them were rewritten to the flat bundle; image links were removed.
The catalogue's sample code was not bundled.
