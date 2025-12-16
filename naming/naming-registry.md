# NUBANC NAMING REGISTRY

All names in the Nubanc system must follow the rules defined here.
Names are part of the system contract and may not be changed casually.

---

## 1. ENVIRONMENTS

Allowed values:
- dev
- staging
- prod

No other environment names are permitted.

---

## 2. TENANT IDENTIFIERS

Format:
tenant_<lowercase_alphanumeric>

Examples:
- tenant_acme
- tenant_nubanc

Tenant identifiers are immutable once assigned.

---

## 3. EVENT NAMES

Format:
<domain>.<fact>.occurred.v<version>

Rules:
- Facts only, no commands
- Past tense
- Versioned

Examples:
- raw.payload.received.v1
- decision.credit_stage.computed.v1
- execution.ledger.posted.v1

---

## 4. DECISION NAMES

Format:
decision.<domain>.<purpose>.v<version>

Examples:
- decision.credit_stage.v1
- decision.limit_assignment.v2

---

## 5. EXECUTION NAMES

Format:
execution.<domain>.<action>.v<version>

Examples:
- execution.ledger.post.v1
- execution.notification.send.v1

---

## 6. DATA ARTIFACTS

Format:
<class>.<domain>.<meaning>.v<version>

Examples:
- raw.credit_application.v1
- ledger.credit_decision.v1
- audit.credit_explanation.v1

---

## 7. IDENTITIES

Format:
nubanc-<domain>-<purpose>-<env>

Examples:
- nubanc-decision-credit-prod
- nubanc-execution-ledger-staging

---

## 8. FILE SYSTEM STRUCTURE

All persisted artifacts must follow:
memory/<class>/<YYYY>/<MM>/<DD>/<id>.json

No deviations allowed.

