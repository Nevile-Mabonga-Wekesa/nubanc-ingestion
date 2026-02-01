# IDENTITY & ACCESS LAW

## 1. IDENTITY TYPES

The NUBANC system recognizes four identity classes:

1. Human Identity
2. Service Identity
3. System Identity
4. Tenant Identity

Every action must be attributable to exactly one identity.

---

## 2. IMMUTABILITY

- Identities are immutable once issued
- Identity identifiers are never reused
- Revocation does not delete identity history

---

## 3. AUTHENTICATION

Authentication proves identity ownership.
Authentication mechanisms are replaceable.
Identity meaning is not.

---

## 4. AUTHORIZATION

Authorization is capability-based, not role-based.

Identities are granted explicit capabilities.
Absence of a capability is denial.

---

## 5. ENVIRONMENT ISOLATION

Identities are environment-scoped.
An identity valid in one environment has no authority in another.

---

## 6. AUDITABILITY

Every authenticated action must be:
- Attributable
- Timestamped
- Environment-scoped
- Tenant-scoped

