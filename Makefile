PYTHON ?= python3

.PHONY: validate test inventory

validate:
	$(PYTHON) scripts/validate_repo.py

test:
	$(PYTHON) -m unittest discover -s tests -v

inventory:
	$(PYTHON) skill/career-desk/scripts/inventory.py examples/sample_project
