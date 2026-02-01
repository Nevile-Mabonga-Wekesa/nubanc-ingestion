# NUBANC SYSTEM

This repository defines the foundational laws, structures, and contracts
of the Continuum system.

This is not an application repository.
This is the canonical source of truth for:
- System principles
- Event contracts
- Decision boundaries
- Execution separation
- Infrastructure shape

All systems built from this repository must:
- Be replayable
- Be deterministic
- Be auditable
- Separate decision from execution

If it is not defined here, it does not exist.

cat <<EOF > README.md
# Nubanc Ingestion API

Event-driven ingestion and normalization service.

## Tech Stack
- Python 3.11
- FastAPI
- Pydantic
- SQLAlchemy

## Local Setup

\`\`\`bash
pyenv install 3.11.9
pyenv local 3.11.9
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
\`\`\`

## Run API

\`\`\`bash
uvicorn contracts.api.main:app --reload
\`\`\`

## API Docs
- Swagger UI: http://localhost:8000/docs

## Ingestion Model
- Async ingestion
- Event-based tracking
- Status polling via event_id

EOF

