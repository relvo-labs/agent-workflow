# Security

This offline toolkit does not sandbox agents, authenticate authorization declarations,
verify evidence truth, enforce locks or prevent omitted work. Never execute command
strings from a bundle. Inspect third-party skills as untrusted input. Keep real
credentials, private payloads and machine-local adoption files out of public reports.

No supported production release exists yet; only the current Draft is maintained.
For a vulnerability, use GitHub's private vulnerability reporting **if the repository
UI offers it**. No private reporting endpoint is asserted to be enabled. If unavailable,
open a public issue asking for a private contact, without exploit details, secrets or
sensitive payloads; wait for a maintainer to establish a channel before sending them.
There is no response-time SLA. Do not publish an unpatched sensitive finding in an
ordinary issue or PR. Parser diagnostics intentionally print stable codes, not input.
