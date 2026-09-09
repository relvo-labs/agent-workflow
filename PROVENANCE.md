# Provenance and licenses

The workflow prose, skills, schemas, semantic code, fixtures and diagram source were
independently authored for Relvo Agent Workflow. No third-party skill text, private
transcript, private evidence file or provider implementation is redistributed.
Synthetic fixture identities/timestamps are examples, not observations of a provider.
Repository content is Apache-2.0 unless a file explicitly states otherwise.

## Referenced standards and tools

| Source | License / use | Redistribution |
|---|---|---|
| https://json-schema.org/draft/2020-12 | JSON Schema specification; specification text under its published license | URI reference only; no specification text copied |
| https://github.com/python-jsonschema/jsonschema | MIT | Installed dependency, not vendored |
| https://github.com/python-attrs/attrs | MIT | Installed transitive dependency, not vendored |
| https://github.com/python-jsonschema/jsonschema-specifications | MIT | Installed transitive dependency, not vendored |
| https://github.com/python-jsonschema/referencing | MIT | Installed transitive dependency, not vendored |
| https://github.com/crate-py/rpds | MIT | Installed transitive dependency, not vendored |
| https://docs.astral.sh/uv/ | Tool implementation MIT/Apache-2.0; documentation referenced only | No copied documentation |
| https://www.apache.org/licenses/LICENSE-2.0 | Apache-2.0 | LICENSE bootstrapped from GitHub's Apache template |

Dependency versions are pinned in requirements.txt; installed distribution metadata
is checked during local validation/review. Provider names identify target consumers; no native integration is implemented.
The following official pages inform original, short discovery notes only. Their
redistribution licenses/website terms have **not** been cleared; no upstream skill,
example, template or documentation passage is copied. The project license does not
relicense these sources:

- Agent Skills format: https://agentskills.io/specification
- Codex discovery: https://developers.openai.com/codex/skills
- Claude Code discovery: https://code.claude.com/docs/en/skills
- Hermes discovery/trust: https://hermes-agent.nousresearch.com/docs/user-guide/features/skills

Documentation review is not a runtime probe. Additional sources must record URL,
license/provenance and whether any content was copied before they are committed.
