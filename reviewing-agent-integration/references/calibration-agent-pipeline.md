# Calibration fixture: agent-pipeline

Expected verdicts for `~/code/agent-pipeline` at commit `9af07b3` (2026-07-07), taken from the
2026-09-10 baseline review and checked against a separate reading of the source the same day.
Use: run the skill on that repo and diff the verdict column. The table below uses the baseline's
vocabulary; map it to the skill's status vocabulary as follows before diffing:
Implements -> present, fitting or present, adjust; Partial -> present, adjust or misapplied;
Misapplies -> misapplied or absent, needed (stated intent); Lacks -> absent, needed or absent, not
needed; N/A -> not applicable. A difference inside one mapping is not a regression.

Second run (2026-09-10, skill-guided, fixture unseen) agreed on every pattern. Its statuses:
checkpoint-resume misapplied; exception-handler-chain, tool-provider, dead-letter-agent,
prompt-firewall absent (the last two "not needed" by when-to-avoid); least-privilege-tool-scope,
reflection-loop, llm-as-judge, context-injection present, adjust; pipeline present, fitting;
content-based-router, direct-message, orchestrator, idempotent-agent, peer-to-peer-delegation
not applicable (rejected scanner candidates); the remaining fifteen not applicable. Update this file only when a
difference is shown to be a fixture error, and say why in the commit.

## 2. Verdict table

Verdict vocabulary: **Implements** (present and matches the catalogue's solution); **Partial** (present, but a load-bearing part of the catalogue's solution is missing); **Misapplies** (present under the pattern's name but not doing what the pattern does); **Lacks** (absent, and the catalogue or the codebase's own design says it should be there); **N/A** (absent, and the catalogue's "When to avoid" or the codebase's context says it should not be there).

| #   | Pattern                    | Category       | Verdict                                       | Fits stated intent?                                                     | Fits implementation?                                                             | Section |
| --- | -------------------------- | -------------- | --------------------------------------------- | ----------------------------------------------------------------------- | -------------------------------------------------------------------------------- | ------- |
| 1   | Direct Message             | messaging      | Implements                                    | yes                                                                     | yes                                                                              | 3.1     |
| 2   | Broadcast Message          | messaging      | N/A                                           | no publishers with unknown subscribers                                  |                                                                                  |         |
| 3   | Blackboard                 | messaging      | N/A (by design), with one boundary bend       | yes                                                                     | mostly                                                                           | 3.2     |
| 4   | Agent Card Registry        | discovery      | N/A                                           | static, in-process topology                                             |                                                                                  |         |
| 5   | Agent Proxy                | discovery      | N/A                                           | one framework, one protocol                                             |                                                                                  |         |
| 6   | Broker                     | discovery      | N/A                                           | one provider per capability                                             |                                                                                  |         |
| 7   | Context Injection          | context        | Implements                                    | yes                                                                     | yes, with two DESIGN §8 knobs unbuilt                                            | 3.3     |
| 8   | Tool Provider              | context        | Misapplies (nominal)                          | claimed                                                                 | no                                                                               | 3.4     |
| 9   | Content-Based Router       | routing        | N/A                                           | one task type; the conditional edge routes on a verdict, not on content |                                                                                  |         |
| 10  | Scatter-Gather             | routing        | N/A, with one latency note                    | stages are data-dependent                                               |                                                                                  | 5       |
| 11  | Pipeline                   | routing        | Implements                                    | yes                                                                     | yes                                                                              | 3.5     |
| 12  | Supervised Delegation      | coordination   | N/A                                           | fixed plan, no runtime re-planning; DESIGN §2 rules it out correctly    |                                                                                  |         |
| 13  | Orchestrator               | coordination   | Implements                                    | naming conflict with DESIGN §2                                          | yes                                                                              | 3.6     |
| 14  | Choreography               | coordination   | N/A                                           | central graph; observability chosen over scale                          |                                                                                  |         |
| 15  | Peer-to-Peer Delegation    | coordination   | N/A                                           | no runtime delegation                                                   |                                                                                  |         |
| 16  | Group Chat                 | coordination   | N/A                                           | reflection loop is the right choice over maker-checker here             |                                                                                  | 3.7     |
| 17  | Magentic                   | coordination   | N/A                                           | plan is knowable in advance                                             |                                                                                  |         |
| 18  | Mediator                   | coordination   | N/A                                           | four agents, linear; no N-squared problem                               |                                                                                  |         |
| 19  | Saga                       | coordination   | N/A                                           | no external side effects to compensate                                  |                                                                                  |         |
| 20  | Dead Letter Agent          | resilience     | Lacks (by documented decision)                | decision is documented                                                  | the decision leaves the failure payload unconsumed                               | 3.8     |
| 21  | Circuit Breaker            | resilience     | Lacks (low priority)                          | not in DESIGN                                                           | provider failures propagate raw through the loop                                 | 3.9     |
| 22  | Checkpoint & Resume        | resilience     | Partial                                       | claimed as done                                                         | in-memory only; resume untested; working memory outside state; no `errors` field | 3.10    |
| 23  | Least-Privilege Tool Scope | security       | Implements                                    | grant table in DESIGN §5 disagrees with `config.py`                     | yes, code-enforced                                                               | 3.11    |
| 24  | Prompt Firewall            | security       | Lacks (severity depends on corpus provenance) | not in DESIGN                                                           | retrieved text reaches the analyst and the judge unsanitised                     | 3.12    |
| 25  | Trust Boundary             | security       | N/A (deferred per edge)                       | yes, DESIGN §4                                                          | yes                                                                              | 3.13    |
| 26  | LLM-as-Judge               | evaluation     | Implements                                    | yes                                                                     | verdict has no reason; judge shares the producer's model                         | 3.14    |
| 27  | Ensemble Judge             | evaluation     | Lacks (not currently warranted)               | not in DESIGN                                                           | single judge; cheap second lens half-exists                                      | 3.15    |
| 28  | Reflection Loop            | evaluation     | Implements                                    | yes                                                                     | yes, with the companion-pattern gaps in 3.8, 3.9, 3.14                           | 3.7     |
| 29  | Idempotent Agent           | implementation | N/A                                           | read-only pipeline                                                      |                                                                                  |         |
| 30  | Exception Handler Chain    | implementation | Lacks                                         | DESIGN §6 promises re-prompt; none exists                               | all non-grounding failures abort on first occurrence                             | 3.16    |

**Counts:** 30 patterns in the catalogue. 14 carry a non-N/A verdict: Implements 7, Partial 1, Misapplies 1, Lacks 5. 16 are marked N/A; 2 of those (Blackboard, Trust Boundary) get a full section anyway because the codebase reasons about them explicitly, and the other 14 get the one-line reason in the table. Net: 16 sections in §3, 14 one-liners.

---


## Verdicts confirmed by the separate reading

- Tool Provider: nominal. `TOOL_CATALOG` in `src/agent_pipeline/config.py` is unreferenced; tools are plan-step names dispatched by branch.
- Human-in-the-loop interrupt: documented in `DESIGN.md` section 10, not built in `src/agent_pipeline/graph/pipeline.py`.
- Checkpoint and Resume: `InMemorySaver` default, no resume path.
- Dead Letter, Circuit Breaker, Exception Handler Chain: absent.
- A2A: declined by design in `DESIGN.md` section 4; not applicable.

## Third run (2026-09-10, installed skill, fixture unseen)

Inside budget at 4,487 words. Agreed with the fixture on every pattern except Tool Provider, which
it marked "absent, not needed" because the when-to-avoid clause applies. That exposed a missing
rule, now in SKILL.md: a design claim the code lacks is "absent, needed" or "misapplied", never
"not needed". Expected Tool Provider status: absent, needed (stated intent in `DESIGN.md` section 5;
`TOOL_CATALOG` in `src/agent_pipeline/config.py` unreferenced), recommendation build or remove the
claim. Checkpoint and Resume may be "present, adjust" or "misapplied"; both are inside the mapping.

## Fourth run (2026-09-10, after the design-claim rule)

4,435 words. Tool Provider: absent, needed, remove the claim. Checkpoint and Resume: misapplied,
narrow the claim. Both as expected. Every other verdict inside the mapping. Six wording
inconsistencies reported and fixed in SKILL.md the same day; those fixes have not yet been run
against this fixture. Next edit to the skill or scanner: run the review and diff before trusting it.

## Fifth run (2026-09-11, after the scale fixes)

4,497 words for 1,494 source lines (budget 3,000 to 4,500). Companions moved to section 7 as
intended. Tool Provider: misapplied, narrow the claim (inside the mapping). Checkpoint: misapplied.
New: Ensemble Judge "absent, needed" through the failure-map test (FM-3.3 open, Ensemble Judge its
only ✅ mitigator). Acceptable; the rule was then tightened to ✅ mitigators of exhibitable modes, one
pattern per open mode, which still yields this verdict. Four wording contradictions fixed the same
day (findings order, misapplied versus absent when a mechanism is half built, the failure-map test,
word counting); not yet rerun against this fixture.
