# Workflow contract 0.1 (Draft)

This is an offline, skills-first collaboration contract, not a workflow engine,
provider runtime, process supervisor, safety sandbox or A2A wire replacement.
Normative MUST rules below apply to submitted records; a validator cannot enforce
what an operator omits or fabricates.

## Sequence and roles

The [decision data](../diagrams/core.json) is the source for the generated diagram.
Requester supplies need and authority; coordinator classifies, checks DAG and
leases, assigns minimal context and closes correlated outcomes. Worker owns one
bounded outcome. Terminal runs literal commands. Reviewer inspects frozen evidence;
human owns merge decisions. S low-risk work MAY stay entirely with the coordinator.
High risk with explicit sufficient authority MAY proceed without repetitive ASK.
Only missing/ambiguous authority or a material unresolved choice requires a question.

Tasks move through authorization → classification → dependency/resource gate →
identity/context → run/questions/controls/checkpoint → correlated outcome → evidence
review → delivery or one bounded repair → blocked. Development MAY add PR, review,
merge, deploy and UAT only when those side effects are separately authorized.

## Versioned record model

[TaskPacket](../schemas/0.1/task-packet.schema.json) owns request, authority,
classification, exact identity, optional development candidate SHA, DAG and acceptance IDs.
[Checkpoint](../schemas/0.1/checkpoint.schema.json) records the runtime observation,
queue cancellation, process state, history persistence, durability and next action.
[Result](../schemas/0.1/result.schema.json) binds outcome and embedded Evidence.
[ControlReceipt](../schemas/0.1/control-receipt.schema.json) is the latest snapshot
per unique control, not an event stream. [Bundle](../schemas/0.1/bundle.schema.json)
is the offline validation input with all four correlated records.
Unknown fields and versions fail closed. IDs are opaque non-empty strings; Git
identities use lowercase 40-character SHA-1 IDs in v0.1 (SHA-256 repositories are
not supported). Pre-PR identity uses `pre-pr:<branch>`; once assigned, update all
records to the actual PR. A receipt cannot silently change task/run/provider/session.
Every identity requires provider and exact session. Generic non-repository tasks
MAY omit all repository/worktree/branch/base/issue/PR fields and candidate; no
placeholder Git identity is needed. Supplying any development identity field
requires the complete extension. Development task/result/evidence MUST include
a candidate SHA. If generic work supplies a candidate, task/result/evidence MUST
all supply the same SHA; omission is not permission to accept stale evidence.

## Identity, DAG and leases

One provider/session MUST have one consistent identity within the submitted DAG.
For development it MUST bind one repository/worktree/branch/base/issue/PR tuple;
development nodes declaring writes MUST NOT omit the development extension.
Different PRs MUST NOT share the writer even serially or in the same phase. A fresh
session can replace a writer only after prior quiescence and explicit acknowledged
handoff. No submitted running node may match the prior exact provider/session,
regardless of its write paths or a blocked result. For development the from/to
repository, branch, base, issue and PR remain the same; generic handoffs omit that
extension on both sides. One writer is governance,
not an OS mutex or distributed lock. The submitted DAG is the scope of overlap
checks; unseen processes and other bundles are outside the validator's visibility.
Node dependencies MUST be present and acyclic; running/completed nodes MUST have
completed prerequisites. Concurrent writes conflict on path equality/ancestry;
exclusive resources conflict on exact keys. Paths use canonical relative POSIX
syntax, without empty, dot, parent, backslash, drive or absolute components.
Resource naming and repository root interpretation are team obligations.

## Stages and closure

Persisted ≠ observed ≠ applied. In this snapshot contract observed implies persisted,
and applied implies observed; providers with different event ordering must buffer
until a valid snapshot exists. Unique receipt IDs/control IDs and increasing sequence
numbers prevent replay *inside one bundle*, not across a durable external ledger.
A queue cancellation is not proof of zero processes. A cancelled result MUST show
quiescence. Persisted history never makes inflight or unknown work durable.
Native resume MUST be positively supported, otherwise produce a blocked checkpoint;
fresh-session transfer is not native resume. CLI configuration is not native-resolved
model/effort evidence. No adapter in v0.1 has a real provider probe.

Result outcomes are delivered, blocked or cancelled; running/paused checkpoints are
intermediate records, not valid terminal bundles. Delivered requires completed DAG,
quiescence, candidate match when present and passing evidence for every acceptance ID.
Evidence command strings are inert and MUST NOT be executed from untrusted input.
External evidence MUST have an exact target and a readback reference. The validator
checks the declaration, not network state, command execution, truth, freshness by
wall clock or provenance signatures. Candidate equality is the v0.1 stale-evidence
rule when a candidate is supplied. Generic evidence without a candidate is bound
by its containing result's task/run/identity and acceptance IDs, not an invented
Git SHA; the reviewer decides whether observations are current enough.
Repair attempts MUST not exceed the task's limit, at most one. Remaining failures
MUST stop blocked with reason and next action. Valid does not mean safe, approved,
independently reviewed or ready to merge. Ready grants no merge authority.

## Team profiles and compatibility

[Default profile](../profiles/default.json) is a template: copy choices into a TaskPacket.
The validator does not silently load machine/team policy. Models, quota and timebox
are deliberately unset; the team must decide them before execution when material.
The validator enforces the hard v0.1 ceiling of one repair and does not execute tasks.
Changing field meaning requires a new version; additive fields also require a
version because unknown fields are rejected. Keep 0.1 schemas immutable after release.
