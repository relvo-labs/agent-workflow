# Contributing

Open an issue describing the behavior, acceptance and compatibility impact; check
existing issues/PRs first. Use one focused working branch and a Draft PR. Keep original
skills small and name ownership/counter-triggers. Contracts, semantic tests, fixtures
and docs change together. Never add private logs, credentials or machine paths.

Install pinned dependencies with the README command, then run:

```sh
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python tools/generate_diagram.py --check
git diff --check
```

Tests are offline. Add a negative fixture for the exact rejected behavior; do not
count an unrelated schema error as semantic proof. Public sources need URLs, license
and a note about copied versus independently authored content in PROVENANCE.md.
Changes are contributed under Apache-2.0. No CLA is currently required.
A fresh reviewer should inspect the frozen head. Human review and merge are required;
Ready never grants merge permission. Do not poll hosted Actions or add push/opened
triggers. No committed screenshots, completion PDFs or private evidence reports.
