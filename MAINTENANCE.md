# Maintenance

Maintainers triage issues and compatibility changes manually. No response SLA,
scheduled job, release automation or hosted CI is installed. Local tests are the
baseline gate; an independent reviewer and a human merge decision are separate gates.

Before release: freeze schema version, review negative coverage, review dependency
licenses and security, rerun clean quickstart/adoption, test intended OS/provider
versions, document evidence and obtain human approval. Release is outside this Draft.
Update dependencies deliberately through `uv pip compile requirements.in -o requirements.txt`;
review the entire lock diff and rerun the suite. Rollback an unmerged change by closing
its PR; merged rollback requires an ordinary reviewed revert PR.

Priorities: stricter real-world evidence provenance, provider-native capability probes,
cross-bundle writer/receipt ledger design, and adoption usability feedback. None of
these are implied by a passing offline bundle today.
