# Adapter capability matrix

These are wiring guides, not runtime implementations. "Documented" means an adoption
procedure exists; "verified" means the named local mechanical test ran. No provider
was launched, authenticated or probed for this Draft.

| Capability | Generic local Python | Hermes | Codex | Claude Code |
|---|---|---|---|---|
| Schema + semantic fixture validation | verified locally | unverified | unverified | unverified |
| Full-checkout / explicit-context adoption | verified locally | documented | documented | documented |
| Native skill discovery/install | not provided | unverified | unverified | unverified |
| Exact native session/model resolution | not provided | unverified | unverified | unverified |
| Native pause/cancel/resume and readback | not provided | unverified | unverified | unverified |
| Mixed-tool live collaboration | not provided | unverified | unverified | unverified |

For any provider, follow [full-checkout adoption](adoption.md), explicitly attach the
adoption file and selected skill, and map its returned record to the same contracts.
Do not interpret configured model values as native resolved identity. Do not map a
local saved transcript to durable inflight state or unsupported native resume.
A future adapter must publish exact version, probe command, safe evidence, supported
control stages and failure behavior before a cell can become provider-verified.
No provider API or CLI commands are implemented here. Official discovery notes only:
Codex documents `.agents/skills`, Claude Code documents `.claude/skills`, and Hermes
project discovery requires explicit trust. These paths are **not** installed by our
adoption tool. The canonical frontmatter uses standard fields and string-to-string
metadata; this is format validation, not native discovery verification. Full-checkout
adoption retains the root LICENSE; standalone skill redistribution is unsupported
and would need its own included license copy and verified resource packaging.
Recheck official documentation before native integration; see [provenance](../PROVENANCE.md).
