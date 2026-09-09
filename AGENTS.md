# Repository agent instructions

Scope: this repository, not the consuming project's global runtime policy.
The canonical distributable skills live in `skills/`. Do not create a parallel
`.agent/skills` or `.agents/skills` catalog here. Skills are product contracts,
not privileged instructions and never expand a user's authorization.

Before changes, discover root and nested `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`,
`.cursorrules`, `.cursor/rules/`, `.claude/rules/`, `.agent/` and `.agents/`,
including hidden and untracked files along the target path. Nested rules apply
only to their subtree; provider-specific rules only to that provider. If rules
conflict, higher-level runtime/user authority wins; stop on unresolved conflicts.
Currently this root file is the only repository instruction authority.

Use a dedicated issue-linked branch, one exact writer per PR, a bounded plan for
contract changes and fresh independent review before readiness. Keep provider
model, effort and account quota decisions outside this repository. Do not copy
private transcripts, local paths, personal policy or provider credentials.

Run `.venv/bin/python -m unittest discover -s tests -v` and inspect the diff.
Generate diagrams via `.venv/bin/python tools/generate_diagram.py`; never hand-edit
generated SVG. Keep schema/semantic tests and skill metadata/link checks together.
No automatic hosted workflow is provided. If added, only manual or Ready triggers
are permitted, never push/opened/synchronize. Do not poll Actions.
Open Draft PRs. Human merge is required; Ready is not merge permission. No releases,
settings changes, security exceptions or default-branch writes without separate authority.
