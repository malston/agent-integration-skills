#!/usr/bin/env python3
"""Scan a codebase for candidate agent-integration patterns.

Why: the review skill must not claim a pattern is present without a file and line.
This script finds candidates by signature so the reviewer confirms or rejects each
one against the pattern's Solution section instead of guessing from memory.
A hit is a candidate, never a verdict: a retry loop is not a circuit breaker.

When: run first in every review. Run again after edits to see what changed.

Usage:
  scan_patterns.py <repo-path> [--json out.json] [--max-hits N] [--show PATTERN]
                   [--include-tests] [--help]

Output: one line per pattern with the hit count and the first few locations.
Use --json for the full machine-readable result and --show <pattern-id> to print
every match for one pattern with context. Exit 0 on success, 2 on bad input,
3 if ripgrep is missing.
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

# pattern id -> (category, [regexes], note for the reviewer)
# Regexes are ripgrep (Rust) syntax, case-insensitive. Keep them specific enough
# that a hit is worth a human look; the reviewer does the rest.
SIGNATURES: dict[str, tuple[str, list[str], str]] = {
    # messaging
    "direct-message": ("messaging", [
        r"tasks/send|send_task\(|delegate\(|send_message\(|\.send\(\s*\w*agent|dispatch\.\w+|/dispatch/|runtime_url|agent_url",
    ], "point-to-point call between agents or to a worker"),
    "broadcast-message": ("messaging", [
        r"publish\(|\.subscribe\(|pubsub|topic\s*=|EventBus|event_bus",
    ], "publish or subscribe on a shared channel"),
    "blackboard": ("messaging", [
        r"blackboard|shared_state|SharedState|shared_memory|class\s+\w*State\(TypedDict\)",
    ], "shared mutable state read and written by several agents"),
    # discovery
    "agent-card-registry": ("discovery", [
        r"\.well-known/agent\.json|AgentCard|agent_card|capabilit(y|ies)_registry|register_agent\(",
    ], "capability manifest or registry lookup"),
    "agent-proxy": ("discovery", [
        r"class\s+\w*Proxy\w*|reverse_proxy|forward_to\(|upstream_url",
    ], "intermediary that forwards to an agent"),
    "broker": ("discovery", [
        r"\bBroker\b|message_broker|kafka|nats|rabbitmq|amqp|redis\.Streams|xread",
    ], "message broker in the path between agents"),
    # context
    "context-injection": ("context", [
        r"assemble_context|build_context|context_window|system_prompt\s*=|_SYSTEM\s*=|SYSTEM_PROMPT|SystemMessage\(|inject(ed)?_context|shortlist|render_prompt|prompt_context|build_prompt",
    ], "harness assembles context before the model call"),
    "tool-provider": ("context", [
        r"list_tools|tools/list|tools/call|call_tool\(|@\w*\.tool\b|mcp\.server|from mcp|McpServer|ToolRegistry|register_tool|TOOL_CATALOG|tool_catalog|\bTool\(",
    ], "tools exposed through a registry or MCP server"),
    # routing
    "content-based-router": ("routing", [
        r"add_conditional_edges|def route\(|def router\(|route_by|classify_complexity|dispatch_table",
    ], "runtime routing on message content"),
    "pipeline": ("routing", [
        r"add_edge\(|\bPipeline\b|def run_pipeline|stages?\s*=\s*\[|RunnableSequence",
    ], "fixed sequential stages"),
    "scatter-gather": ("routing", [
        r"asyncio\.gather\(|ThreadPoolExecutor|fan_out|fanout|gather_results|parallel_review",
    ], "fan out to several agents, gather results"),
    # coordination
    "orchestrator": ("coordination", [
        r"class\s+\w*Orchestrator\w*|orchestrat|master_plan|task_plan",
    ], "one component owns the plan and the sequence"),
    "choreography": ("coordination", [
        r"on_event\(|@\w+\.on\(|event_handler|handle_event\(|reacts_to",
    ], "agents react to events without a central owner"),
    "supervised-delegation": ("coordination", [
        r"create_supervisor|Supervisor\b|supervisor_node|worker_agents|delegate_to\(",
    ], "supervisor assigns and monitors workers"),
    "peer-to-peer-delegation": ("coordination", [
        r"handoff\(|transfer_to_|Handoff\b|swarm",
    ], "agent hands the task to a peer directly"),
    "group-chat": ("coordination", [
        r"GroupChat|group_chat|round_robin|speaker_selection|next_speaker",
    ], "turn-taking among several agents"),
    "mediator": ("coordination", [
        r"class\s+\w*Mediator\w*|\bmediat(or|ion|es)\b",
    ], "a mediator resolves between agents"),
    "magentic": ("coordination", [
        r"task_ledger|progress_ledger|Magentic|stall_count|stall_detect",
    ], "dynamic task ledger with stall detection"),
    "saga": ("coordination", [
        r"compensat|rollback\(|undo_|Saga\b|compensating_action",
    ], "forward action paired with a compensating action"),
    # resilience
    "checkpoint-resume": ("resilience", [
        r"checkpointer|Checkpointer|InMemorySaver|SqliteSaver|PostgresSaver|save_checkpoint|resume_from|thread_id",
    ], "state persisted between steps for resume"),
    "circuit-breaker": ("resilience", [
        r"CircuitBreaker|circuit_breaker|HALF_OPEN|half_open|failure_threshold|probe_(job|call|request)|revive|cooldown",
    ], "stateful breaker around a failing dependency; a probe without an open state is a partial hit"),
    "dead-letter-agent": ("resilience", [
        r"dead_letter|DeadLetter|dlq|unprocessable|escalate_to_human|human_review_queue",
    ], "failed tasks routed to a handler, never dropped"),
    # implementation
    "exception-handler-chain": ("implementation", [
        r"class\s+\w*Error\(Exception\)|class\s+\w*Violation\(Exception\)|error_type|ErrorCode|handler_chain|FailoverReason",
    ], "typed errors handled by class, in order"),
    "idempotent-agent": ("implementation", [
        r"idempoten|already_done|seen_keys|@guard\.protect|idempotency_key",
    ], "stable key so a retry causes no duplicate effect"),
    # security
    "trust-boundary": ("security", [
        r"TrustLevel|TrustTier|trust_level|UNTRUSTED|classify_caller|bearer|OAuth|oauth|Authorization:",
    ], "callers tiered and authenticated before tasks are accepted"),
    "least-privilege-tool-scope": ("security", [
        r"allowed_tools|TOOL_GRANT|tool_grant|allowlist|allow_list|scoped_tools|PermissionError",
    ], "tool access limited per agent at the server"),
    "prompt-firewall": ("security", [
        r"prompt_injection|prompt.injection|sanitize\(|firewall|\[BLOCKED\]|untrusted_content|injection_guard",
    ], "external content inspected before it reaches context"),
    # evaluation
    "reflection-loop": ("evaluation", [
        r"critic|critique|refine\(|reflect|MAX_\w*ATTEMPTS|feedback\s*=|regenerate",
    ], "output criticized and regenerated with feedback"),
    "llm-as-judge": ("evaluation", [
        r"judge|verdict|supported\s*[:=]|ClaimVerifier|with_structured_output\(\s*_?\w*Verdict|score_",
    ], "a model judges another output"),
    "ensemble-judge": ("evaluation", [
        r"ensemble|majority_vote|vote\(|quorum|consensus|n_judges|judges\s*=\s*\[",
    ], "several judges combined"),
}

# Topology and transport signals; not patterns, but the reviewer needs them first.
TOPOLOGY: dict[str, list[str]] = {
    "langgraph": [r"from langgraph|StateGraph|add_conditional_edges"],
    "langchain": [r"from langchain"],
    "mcp": [r"from mcp\b|mcp\.server|modelcontextprotocol|mcp_server_url|McpServer|\bMCP\b"],
    "a2a": [r"\ba2a\b|/tasks/send|AgentCard|agent\.json"],
    "grpc": [r"import grpc|grpc\.aio|\.proto\b"],
    "http-server": [r"FastAPI\(|Flask\(|@app\.(get|post)|BaseHTTPRequestHandler"],
    "sse-streaming": [r"text/event-stream|StreamingResponse|EventSourceResponse"],
    "message-broker": [r"kafka|nats|rabbitmq|amqp|redis\.Streams|xread"],
    "human-in-the-loop": [r"interrupt\(|requires_human|human_approver|awaiting_human|HITL|approval"],
    "side-effecting-tools": [r"subprocess\.run|\.post\(|\.put\(|\.delete\(|INSERT INTO|\bUPDATE\s+\w+\s+SET\b|write_file|send_email|charge\("],
    "model-calls": [r"anthropic|openai|init_chat_model|ChatAnthropic|ChatOpenAI|messages\.create\("],
}

DOC_SUFFIXES = {".md", ".rst", ".txt", ".adoc", ".html", ".svg", ".ipynb"}
CONFIG_SUFFIXES = {".toml", ".yaml", ".yml", ".json", ".ini", ".cfg", ".env"}
CODE_SUFFIXES = {".py", ".js", ".ts", ".tsx", ".jsx", ".go", ".rs", ".java", ".kt", ".cs", ".rb",
                 ".php", ".scala", ".swift", ".c", ".cc", ".cpp", ".h", ".hpp", ".sh", ".bash", ".zsh",
                 ".sql", ".proto", ".graphql", ".lua", ".ex", ".exs", ".erl", ".clj", ".hs", ".ml"}
DEFAULT_GLOBS = ["!**/node_modules/**", "!**/.venv/**", "!**/target/**", "!**/dist/**",
                 "!**/.git/**", "!**/*.lock", "!**/*_pb2*.py", "!**/output/**", "!**/build/**",
                 "!**/vendor/**", "!**/static/**", "!**/*.min.js", "!**/*.ipynb"]
TEST_GLOBS = ["!**/test*/**", "!**/tests/**", "!**/*_test.*", "!**/test_*.*"]


def _source_lines(root: Path, globs: list[str]) -> int:
    """Count lines in source files the scan would search, for the review's word budget."""
    cmd = ["rg", "--files", str(root)]
    for g in globs:
        cmd += ["-g", g]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    total = 0
    for f in proc.stdout.splitlines():
        suf = Path(f).suffix.lower()
        if suf not in CODE_SUFFIXES:
            continue
        try:
            with open(f, "rb") as fh:
                total += sum(1 for _ in fh)
        except OSError:
            continue
    return total


def rg(pattern: str, root: Path, globs: list[str]) -> list[dict]:
    cmd = ["rg", "--json", "-i", "-e", pattern, str(root)]
    for g in globs:
        cmd += ["-g", g]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    hits = []
    for line in proc.stdout.splitlines():
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue
        if obj.get("type") != "match":
            continue
        d = obj["data"]
        hits.append({
            "file": str(Path(d["path"]["text"]).relative_to(root)),
            "line": d["line_number"],
            "text": d["lines"]["text"].rstrip("\n")[:160],
            "kind": ("doc" if Path(d["path"]["text"]).suffix.lower() in DOC_SUFFIXES
                     else "config" if Path(d["path"]["text"]).suffix.lower() in CONFIG_SUFFIXES
                     else "code"),
        })
    return hits


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("repo", help="path to the codebase")
    ap.add_argument("--json", dest="json_out", help="write full results to this file")
    ap.add_argument("--max-hits", type=int, default=3, help="locations to print per pattern (default 3)")
    ap.add_argument("--show", help="print every match for one pattern id")
    ap.add_argument("--include-tests", action="store_true", help="scan test files too (off by default)")
    args = ap.parse_args()

    if shutil.which("rg") is None:
        print("error: ripgrep (rg) is required. brew install ripgrep", file=sys.stderr)
        return 3
    root = Path(args.repo).expanduser().resolve()
    if not root.is_dir():
        print(f"error: {root} is not a directory", file=sys.stderr)
        return 2
    globs = list(DEFAULT_GLOBS) + ([] if args.include_tests else TEST_GLOBS)

    result = {"repo": str(root), "topology": {}, "patterns": {}}
    for key, pats in TOPOLOGY.items():
        hits = []
        for p in pats:
            hits += rg(p, root, globs)
        result["topology"][key] = hits
    for pid, (cat, pats, note) in SIGNATURES.items():
        hits = []
        for p in pats:
            hits += rg(p, root, globs)
        seen = set()
        uniq = []
        for h in hits:
            k = (h["file"], h["line"])
            if k not in seen:
                seen.add(k)
                uniq.append(h)
        uniq.sort(key=lambda h: (h["file"], h["line"]))
        result["patterns"][pid] = {"category": cat, "note": note, "hits": uniq}

    if args.show:
        if args.show in result["patterns"]:
            entry = result["patterns"][args.show]
            print(f"{args.show} ({entry['category']}): {entry['note']}")
            hits = entry["hits"]
        elif args.show in result["topology"]:
            print(f"{args.show} (topology signal)")
            hits = result["topology"][args.show]
        else:
            print(f"error: unknown pattern or topology id {args.show!r}", file=sys.stderr)
            return 2
        for h in hits:
            print(f"  [{h['kind']}] {h['file']}:{h['line']}: {h['text']}")
        return 0

    loc = _source_lines(root, globs)
    print(f"repo: {root}")
    print(f"source lines (code suffixes only; tests excluded unless --include-tests): {loc}")
    print("\ntopology signals (files with at least one hit):")
    for key, hits in result["topology"].items():
        files = sorted({h["file"] for h in hits})
        code_files = {h["file"] for h in hits if h["kind"] == "code"}
        mark = "yes" if code_files else ("doc" if files else "no ")
        code = sorted({h["file"] for h in hits if h["kind"] == "code"})
        print(f"  {mark}  {key:<20} {len(code)} code file(s), {len(files) - len(code)} doc file(s)"
              + (f"  e.g. {code[0]}" if code else (f"  e.g. {files[0]}" if files else "")))
    print("\ncandidate patterns (code/doc/config hits; hits are candidates, not verdicts):")
    print("  a pattern with doc hits and no code hits is stated intent, not implementation")
    by_cat: dict[str, list[str]] = defaultdict(list)
    for pid, entry in result["patterns"].items():
        by_cat[entry["category"]].append(pid)
    for cat in ["messaging", "discovery", "context", "routing", "coordination",
                "resilience", "implementation", "security", "evaluation"]:
        print(f"  [{cat}]")
        for pid in by_cat[cat]:
            hits = result["patterns"][pid]["hits"]
            code = [h for h in hits if h["kind"] == "code"]
            docs = sum(1 for h in hits if h["kind"] == "doc")
            cfg = len(hits) - len(code) - docs
            shown = code[:args.max_hits] or hits[:args.max_hits]
            locs = ", ".join(f"{h['file']}:{h['line']}" for h in shown)
            more = f" (+{len(code) - args.max_hits} more code)" if len(code) > args.max_hits else ""
            print(f"    {len(code):>3}/{docs:<3}/{cfg:<2} {pid:<28} {locs}{more}")
    print("\nnext: confirm each candidate against references/patterns/<id>.md, Solution section;")
    print("      use --show <id> for every match with context; --json for the full result.")

    if args.json_out:
        Path(args.json_out).write_text(json.dumps(result, indent=2))
        print(f"\nfull results: {args.json_out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
