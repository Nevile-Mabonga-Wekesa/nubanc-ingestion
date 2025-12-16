# SYSTEM BOUNDARIES

The Nubanc system is composed of the following immutable domains:

- Event Ingress Domain  
Responsible only for recording facts.

- Memory Domain  
Responsible only for preserving truth.

- Decision Domain  
Responsible only for computing outcomes.

- Execution Domain  
Responsible only for acting on decisions.

- Observability Domain  
Responsible only for visibility and evidence.

No domain may assume responsibilities of another.
Cross-domain interaction occurs only through explicit contracts.

