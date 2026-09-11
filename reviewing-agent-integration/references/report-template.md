# Agent Integration Review: <codebase name>

Reviewed <YYYY-MM-DD> against the Agents Integration Patterns catalogue (Hohpe and Woolf lineage;
Brasil, CC BY 4.0; catalogue commit in `references/SOURCE-COMMIT.txt`).
Scope: <path>, commit `<sha>`. Scan: `scan_patterns.py` output attached as `<file>`.

Evidence tags. `[CODE file:line]` read in source. `[DOC file:line]` stated in the codebase's own
documents. `[SCAN n/m/k]` scanner candidates: code, doc, and config hits, before confirmation.
`[CATALOGUE pattern §section]` quoted from the catalogue. `[JUDGMENT]` the reviewer's inference.

## 1. Intent

What the codebase says it is, in its own words, with citations. Which rung of the complexity ladder
it claims: direct model call, single agent with tools, or multiple agents. Which topology it claims:
pipeline, orchestrator, supervisor and workers, choreography, other.

## 2. Implementation

What the code actually is: the rung and topology the code implements, with citations. Where 1 and 2
disagree, say so here in one sentence each; those disagreements are the review's most important
findings and each gets a row in section 4.

## 3. Forces this codebase weights

From `FORCES.md`. Name the forces the codebase's context weights and the evidence for each
(regulated data weights F5 and F7; a batch job weights F8 over F1; an interactive assistant the
reverse). Name the forces it does not weight. Every verdict in section 4 must refer back to this list.

## 4. Findings, one per pattern

Order: misapplied; absent, needed; present, adjust; present, fitting. Absent-not-needed companions,
rejected scanner candidates, and not-applicable patterns get one line each in section 7, no more.

### <Pattern name> (<category>, <maturity>, from references/matrix.md)

- Status: misapplied | absent, needed | present, adjust | present, fitting
- Evidence: `[SCAN n/m/k]`; confirmed at `[CODE file:line]` ... or "no code hit; doc hit at `[DOC file:line]` is intent only"
- What the catalogue says it solves: `[CATALOGUE <pattern> §Problem]` one sentence.
- Fit to intent: does the stated intent call for this pattern? `[JUDGMENT]` with the force it serves.
- Fit to implementation: does the code as written apply it as the Solution section describes? Name
  the departure if any. `[CODE ...]`
- Forces resolved and introduced here: from section 3, not from the catalogue's generic list.
- Failure modes: which `FAILURE-MAP.md` modes this covers or, if absent, leaves open for this
  topology.
- Transport note: only if `TRANSPORT.md` has something specific to say about this pattern on this
  codebase's transport.
- When to avoid: quote the catalogue's `When to avoid` bullet if it applies here, and say whether it
  does.
- Recommendation: build, adopt, adjust, narrow the claim, remove the claim, remove, or leave. One
  sentence. For build, adopt, or adjust: the force it buys and the force it spends, or "spends none"
  for a documentation-only change.

## 5. Failure map for this topology

Table: MAST failure mode, mitigated by (pattern present at `[CODE]`) or open. Only modes the
topology can exhibit; omit the rest.

## 6. Transport

The transports in use `[CODE]`, what the catalogue recommends for the patterns present, and any
warning that applies (fan-out on HTTP/1.1, QUIC replay without idempotency, stdio for remote).
If nothing applies, one sentence saying so.

## 7. Not applicable, rejected candidates, and companions not needed

| Pattern | Scanner hits | Why not here, or leave until (one clause) |

## Sources

The catalogue files read. The codebase files read, with the commit reviewed.

## Not verified

What the review could not establish: behavior under load, untested branches, docs that could not be
reconciled with code, anything inferred rather than read.
