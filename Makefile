PYTHON ?= python3
SKILL_DEST ?=

.PHONY: validate test inventory agent-demo skill-package skill-install

validate:
	$(PYTHON) scripts/validate_repo.py
	$(PYTHON) skill/p2j/scripts/validate_suite.py skill

test:
	$(PYTHON) -m unittest discover -s tests -v

inventory:
	$(PYTHON) skill/p2j/scripts/inventory.py examples/sample_project

agent-demo:
	$(PYTHON) scripts/build_agent_demo.py
	@mkdir -p dist/agent-report
	@for fixture in apps/web/fixtures/*.json; do \
		name=$$(basename "$$fixture" .json); \
		$(PYTHON) apps/web/render_report.py "$$fixture" \
			--output "dist/agent-report/$$name.html"; \
	done

skill-package:
	$(PYTHON) skill/p2j/scripts/install_suite.py --archive dist/project2job-skill-suite-alpha.zip

skill-install:
	@test -n "$(SKILL_DEST)" || (echo "Set SKILL_DEST to your host Skills directory." && exit 2)
	$(PYTHON) skill/p2j/scripts/install_suite.py --dest "$(SKILL_DEST)"
