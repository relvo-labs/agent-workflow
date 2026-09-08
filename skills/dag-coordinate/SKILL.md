---
{
  "name": "dag-coordinate",
  "description": "Use when scheduling dependency-ready work.",
  "license": "Apache-2.0",
  "compatibility": "Requires the complete toolkit checkout and Python 3.11+ with pinned dependencies; no native provider integration is verified.",
  "metadata": {
    "version": "0.1.0",
    "author": "Relvo contributors",
    "related-skills": "task-intake,runtime-checkpoint"
  }
}
---

# dag-coordinate

## When to Use
A task has multiple dependent nodes or shared resources.

Counter-trigger: Do not use to route a trivial single-node S task through extra agents.

## Owns
Dependency and resource scheduling.

## Does not own
A scheduling record is not a process supervisor.

## Inputs
Authorized TaskPacket and current node/lease observations.

## Outputs
Acyclic nodes, ready activation choices or a blocked checkpoint.

## Procedure
1. Name nodes and dependencies; mark completed dependencies only from checked evidence. Refuse missing nodes, cycles and activation ahead of prerequisites.
2. Declare canonical repository-relative write paths and exact exclusive resource keys. Compare active nodes for ancestor-path or resource overlap; queue conflicting work.
3. Choose coordinator for direct bounded work, worker for independent reasoning, terminal for literal bounded commands. A terminal is not a reviewer. Start only ready nodes with an exact identity and smallest sufficient context.
4. Record waiting/running/completed node states and next action. Cross-repository resource keys must be team-canonical. The validator checks only submitted nodes, not hidden workers.

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
A scheduling record is not a process supervisor. Offline examples are synthetic, not provider probes. Relative links resolve inside the full checkout, not inside the target project. Do not copy this file alone; keep the complete checkout and rerun adoption if moved.
