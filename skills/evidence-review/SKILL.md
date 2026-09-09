---
{
  "name": "evidence-review",
  "description": "Use when checking outcomes before closure.",
  "license": "Apache-2.0",
  "compatibility": "Requires the complete toolkit checkout and Python 3.11+ with pinned dependencies; no native provider integration is verified.",
  "metadata": {
    "version": "0.1.0",
    "author": "Relvo contributors",
    "related-skills": "task-intake,runtime-checkpoint"
  }
}
---

# evidence-review

## When to Use
A result is ready for review, repair, delivery or blocked closure.

Counter-trigger: Do not use this check as live external-state verification or independent review.

## Owns
Evidence correlation and bounded closure.

## Does not own
Ready is not authorization to merge, deploy or publish.

## Inputs
TaskPacket, Checkpoint, Result/Evidence and latest ControlReceipts.

## Outputs
Validated delivered/blocked/cancelled bundle plus explicit human decision.

## Procedure
1. Correlate task, run and exact identity across records. Every evidence item names an acceptance ID, actual command or manual check, outcome, target and observation time. Development requires an exact candidate SHA across task, result and evidence. Generic tasks may omit candidate everywhere; if supplied, it must match everywhere.
2. Read external changes back at the exact target using a separately authorized tool. Store a safe evidence reference, not credentials or whole private responses. Offline validation only checks that this reference exists; a reviewer must inspect the observation.
3. Reject stale candidates, duplicate receipts, missing coverage or stage mismatches. Review evidence at the frozen head. If a repair is needed, spend no more than the explicit budget (default one), then recheck invalidated evidence; remaining failure is blocked, never an infinite loop.
4. Deliver only after all acceptance passes and work is quiescent. Report blockers and next owner explicitly. For development only, add PR, fresh review, human merge, deployment and UAT gates when separately authorized; neither schema validity nor Ready grants those actions.

## Relationships
- [task-intake](../task-intake/SKILL.md)
- [runtime-checkpoint](../runtime-checkpoint/SKILL.md)

## Verification
Use the full toolkit checkout referenced in your adoption file. From **any** working directory, run the absolute interpreter/script paths written by `tools/adopt.py`, followed by an absolute bundle path. For example, replace TOOLKIT_ROOT with that checkout:

```sh
TOOLKIT_ROOT/.venv/bin/python TOOLKIT_ROOT/tools/validate.py TOOLKIT_ROOT/examples/happy-path.json
```

On Windows use `TOOLKIT_ROOT/.venv/Scripts/python.exe`. Require exit 0 for a valid bundle, or the specific documented diagnostic for a negative fixture. See [adoption](../../adapters/adoption.md) and [workflow](../../spec/workflow.md).

## Pitfalls
Ready is not authorization to merge, deploy or publish. Offline examples are synthetic, not provider probes. Relative links resolve inside the full checkout, not inside the target project. Do not copy this file alone; keep the complete checkout and rerun adoption if moved.
