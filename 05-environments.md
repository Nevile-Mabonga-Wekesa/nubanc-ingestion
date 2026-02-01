# ENVIRONMENT LAW

The Nubanc system operates in three environments:

- dev
- staging
- prod

Rules:

1. Environments share identical code and contracts.
2. Environments are isolated at the memory and execution layer.
3. Data never flows upward between environments.
4. Decisions must be reproducible across environments given identical input.
5. Production execution has irreversible side effects.
6. Non-production execution is always reversible or simulated.

