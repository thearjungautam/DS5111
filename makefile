ENV = env
PYTHON = $(ENV)/bin/python3
PIP = $(ENV)/bin/pip

default:
	@cat makefile

env:
	python3 -m venv $(ENV)
	$(PIP) install --upgrade pip

update: env
	$(PIP) install -r requirements.txt

lint:
	$(PYTHON) -m pylint bin/ tests/ clean_ids.py

test:
	$(PYTHON) -m pytest -vv tests/

test_enrich:
	@cat mock_transcripts.jsonl | $(PYTHON) -u bin/enrich_transcripts.py | $(PYTHON) bin/validate_schema.py

run:
	@echo "Run pipeline scripts from bin/ as needed."
	@echo "Example: cat input.jsonl | $(PYTHON) -u bin/enrich_transcripts.py"
