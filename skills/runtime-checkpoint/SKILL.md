---
{
  "name": "runtime-checkpoint",
  "description": "Use when recording controls and runtime stops.",
  "license": "Apache-2.0",
  "compatibility": "Requires the complete toolkit checkout and Python 3.11+ with pinned dependencies; no native provider integration is verified.",
  "metadata": {
    "version": "0.1.0",
    "author": "Relvo contributors",
    "related-skills": "writer-handoff,evidence-review"
  }
}
---

# runtime-checkpoint

## When to Use
A running task asks a question, pauses, cancels, resumes or blocks.

Counter-trigger: Do not infer native model resolution or process termination from CLI configuration.

## Owns
Control acknowledgment and checkpoint state.

## Does not own
This skill does not implement provider-native controls.

## Inputs
Task identity, unique control IDs, native observations and next action.

## Outputs
Ordered ControlReceipts plus Checkpoint; blocked if resume is unavailable.

## Procedure
1. For a question state the decision needed, its owner and the next dependency-ready operation; pause only work affected by it. Persist a unique receipt for each control.
2. Use distinct persisted, observed and applied stages. A submitted receipt may claim only the stage supported by native evidence; the bundle contains the latest snapshot per control ID, not duplicate replay entries.
3. On cancellation distinguish queue removal from live processes. Keep unknown/inflight process state explicit; only quiescence permits cancelled closure. Persisted history cannot make inflight work durable.
4. If native resume is unverified or unsupported, fail closed to a blocked checkpoint. A fresh session requires writer-handoff, not a relabeled resume. Always record one concrete next action.

## Relationships
- [writer-handoff](../writer-handoff/SKILL.md)
- [evidence-review](../evidence-review/SKILL.md)

## Verification
Use the full toolkit checkout referenced in your adoption file. From **any** working directory, run the absolute interpreter/script paths written by `tools/adopt.py`, followed by an absolute bundle path. For example, replace TOOLKIT_ROOT with that checkout:

```sh
TOOLKIT_ROOT/.venv/bin/python TOOLKIT_ROOT/tools/validate.py TOOLKIT_ROOT/examples/happy-path.json
```

On Windows use `TOOLKIT_ROOT/.venv/Scripts/python.exe`. Require exit 0 for a valid bundle, or the specific documented diagnostic for a negative fixture. See [adoption](../../adapters/adoption.md) and [workflow](../../spec/workflow.md).

## Pitfalls
This skill does not implement provider-native controls. Offline examples are synthetic, not provider probes. Relative links resolve inside the full checkout, not inside the target project. Do not copy this file alone; keep the complete checkout and rerun adoption if moved.
