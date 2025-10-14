.DEFAULT_GOAL := help

# source: https://stackoverflow.com/questions/18136918/how-to-get-current-relative-directory-of-your-makefile#73509979
MAKEFILE_ABS_DIR := $(dir $(realpath $(lastword $(MAKEFILE_LIST))))

define PRINT_HELP_PYSCRIPT
import re, sys

for line in sys.stdin:
	match = re.match(r'^([.0-9a-zA-Z_-]+):.*?## (.*)$$', line)
	if match:
		target, help = match.groups()
		print("%-30s %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT

.PHONY: help
help:
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

.PHONY: test
test: ## run tests
	pytest
	echo 'To see the coverage report, execute "make view-coverage-report"'

.PHONY: view-coverage-report
view-coverage-report: ## view in the browser the last coverage report generated via "make test"
	python -m webbrowser -t "file:///${MAKEFILE_ABS_DIR}/coverage-report/index.html"
