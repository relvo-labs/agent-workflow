---
{
  "name": "task-intake",
  "description": "Use when turning requests into authorized work.",
  "license": "Apache-2.0",
  "compatibility": "Requires the complete toolkit checkout and Python 3.11+ with pinned dependencies; no native provider integration is verified.",
  "metadata": {
    "version": "0.1.0",
    "author": "Relvo contributors",
    "related-skills": "dag-coordinate,writer-handoff"
  }
}
---

# task-intake

## When to Use
A new request or changed scope needs an explicit decision.

Counter-trigger: Do not use for a completed candidate review; use evidence-review.

## Owns
Authorization and acceptance boundaries.

## Does not own
Task classification is not execution or merge permission.

## Inputs
Request, authorized actor/actions/scopes, acceptance IDs, candidate identity.

## Outputs
TaskPacket with classified risk, acceptance and explicit authorization.

## Procedure
1. List the requested effect, non-goals and exact allowed actions/write scopes. Ask only for missing authority, identity or a decision that changes execution; an explicitly authorized high-risk task is not permanently ASK.
2. Choose S for bounded low-risk work, otherwise M/L for contracts or cross-system effects. S may use the coordinator alone; additional agents must retire a named risk.
3. Bind repository, worktree, branch, immutable base, issue, pre-PR binding or PR, provider and exact session. After PR creation update every correlated record to the actual PR before further execution.
4. Assign acceptance IDs and a candidate SHA. Keep only task-relevant instructions and evidence pointers, never full private chat or credentials. Fill the TaskPacket, then validate the complete example/bundle before activation.

## Relationships
- [dag-coordinate](../dag-coordinate/SKILL.md)
- [writer-handoff](../writer-handoff/SKILL.md)

## Verification
Use the full toolkit checkout referenced in your adoption file. From **any** working directory, run the absolute interpreter/script paths written by `tools/adopt.py`, followed by an absolute bundle path. For example, replace TOOLKIT_ROOT with that checkout:

```sh
TOOLKIT_ROOT/.venv/bin/python TOOLKIT_ROOT/tools/validate.py TOOLKIT_ROOT/examples/happy-path.json
```

On Windows use `TOOLKIT_ROOT/.venv/Scripts/python.exe`. Require exit 0 for a valid bundle, or the specific documented diagnostic for a negative fixture. See [adoption](../../adapters/adoption.md) and [workflow](../../spec/workflow.md).

## Pitfalls
Task classification is not execution or merge permission. Offline examples are synthetic, not provider probes. Relative links resolve inside the full checkout, not inside the target project. Do not copy this file alone; keep the complete checkout and rerun adoption if moved.
