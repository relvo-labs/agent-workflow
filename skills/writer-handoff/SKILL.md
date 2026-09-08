---
{
  "name": "writer-handoff",
  "description": "Use when binding or transferring a writer.",
  "license": "Apache-2.0",
  "compatibility": "Requires the complete toolkit checkout and Python 3.11+ with pinned dependencies; no native provider integration is verified.",
  "metadata": {
    "version": "0.1.0",
    "author": "Relvo contributors",
    "related-skills": "runtime-checkpoint,evidence-review"
  }
}
---

# writer-handoff

## When to Use
Assigning a writer to a PR or replacing a blocked writer.

Counter-trigger: Do not reuse a writer across PRs even in the same phase.

## Owns
Exact writer ownership and transfer.

## Does not own
One writer is governance, not an OS mutex.

## Inputs
Exact previous/current identity, PR binding and quiescence evidence.

## Outputs
Checkpoint handoff with distinct sessions and acknowledged transfer.

## Procedure
1. Bind one provider plus exact session to one repository/worktree/branch/base/issue/PR tuple. Pre-PR uses pre-pr:<branch>; one PR may continue in that exact session.
2. Before transfer stop scheduling and establish prior process quiescence with native evidence. Queue cancellation alone is insufficient. If process state is unknown, block instead of claiming the lease released.
3. Start a fresh session only for the same explicitly transferred work. Record from/to identities, prior_quiescent and acknowledged after the new owner reads the minimal checkpoint. Different PR means a new writer identity, never a resume.
4. Validate the handoff bundle. Keep old-session evidence outside the new correlated result; the current result must bind the current identity. Do not claim distributed exclusion from this record.

## Relationships
- [runtime-checkpoint](../runtime-checkpoint/SKILL.md)
- [evidence-review](../evidence-review/SKILL.md)

## Verification
Use the full toolkit checkout referenced in your adoption file. From **any** working directory, run the absolute interpreter/script paths written by `tools/adopt.py`, followed by an absolute bundle path. For example, replace TOOLKIT_ROOT with that checkout:

```sh
TOOLKIT_ROOT/.venv/bin/python TOOLKIT_ROOT/tools/validate.py TOOLKIT_ROOT/examples/happy-path.json
```

On Windows use `TOOLKIT_ROOT/.venv/Scripts/python.exe`. Require exit 0 for a valid bundle, or the specific documented diagnostic for a negative fixture. See [adoption](../../adapters/adoption.md) and [workflow](../../spec/workflow.md).

## Pitfalls
One writer is governance, not an OS mutex. Offline examples are synthetic, not provider probes. Relative links resolve inside the full checkout, not inside the target project. Do not copy this file alone; keep the complete checkout and rerun adoption if moved.
