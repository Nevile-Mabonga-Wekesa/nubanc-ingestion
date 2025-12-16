# IMMUTABILITY RULE

The following directories are append-only:

- memory/raw
- memory/ledger
- memory/audit

Rules:
- Files may only be created, never modified
- Deletions are forbidden
- Corrections must be new files referencing prior IDs

Violation of these rules invalidates system guarantees.

