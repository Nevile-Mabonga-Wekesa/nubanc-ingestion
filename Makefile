ifndef ENV
$(error ENV is required: dev | staging | prod)
endif

export NUBANC_ENV := $(ENV)


.PHONY: infra-up infra-down check-env

check-env:
	@if [ "$(ENV)" != "dev" ] && [ "$(ENV)" != "staging" ] && [ "$(ENV)" != "prod" ]; then \
		echo "Invalid ENV=$(ENV). Use dev | staging | prod"; \
		exit 1; \
	fi
bootstrap-memory:
	mkdir -p memory/$(ENV)/raw
	mkdir -p memory/$(ENV)/ledger
	mkdir -p memory/$(ENV)/audit

infra-up: check-env bootstrap-memory infra-check start-api
	@echo "Nubanc infra running in $(ENV)"
replay:
	python replay/replay_engine.py

infra-check:
	python replay/replay_engine.py --verify-only

infra-down:
	@echo "Infra shutdown complete"

start-api:
	NUBANC_ENV=dev PYTHONPATH=$(PWD) python -m contracts.api.main

run-api: start-api
