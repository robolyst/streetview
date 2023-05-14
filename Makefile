SHELL := $(shell which bash)
MICROMAMBA := $(PWD)/.micromamba
MAMBA := $(MICROMAMBA)/micromamba
VENV := $(PWD)/.venv
DEPS := $(VENV)/.deps
PROJECT := streetview
PROJECT_DIR = $(PWD)/$(PROJECT)
TEST_DIR = $(PWD)/tests
PYTHON_CMD := PYTHONPATH=$(PWD) $(VENV)/bin/python
COVERAGE := 95  # Required code coverage

ifndef VERBOSE
.SILENT:
endif

.PHONY: help deps clean check format test run demo

help:
	grep -E '^[0-9a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "%-30s %s\n", $$1, $$2}'

$(MAMBA):
	echo "Installing Mamba..."
	$(SHELL) ./install-micromamba.sh "$(MICROMAMBA)"

$(DEPS): environment.yml $(MAMBA)
	echo "Installing dependencies..."
	rm -rf $(VENV)
	$(MAMBA) create --quiet --yes -p $(VENV)
	$(MAMBA) install --quiet --yes --log-level 4 -p $(VENV) -f environment.yml
	cp environment.yml $(DEPS)


deps: $(DEPS)  ## Install project dependencies

clean:  ## Delete unnecessary files from the project
	rm -rf $(MICROMAMBA)
	rm -rf $(VENV)
	rm -rf output.txt
	rm -rf .pytest_cache
	rm -rf .coverage
	rm -rf .mypy_cache
	find . -name __pycache__ | xargs rm -rf

check: $(DEPS)  ## Code style checks (isort, flake8 and mypy)
	- $(PYTHON_CMD) -m isort . --diff
	- $(PYTHON_CMD) -m flake8 $(PROJECT_DIR) $(TEST_DIR)
	- $(PYTHON_CMD) -m mypy -p $(PROJECT) --namespace-packages --check-untyped-defs

format: $(DEPS)  ## Run auto linting
	$(PYTHON_CMD) -m isort .
	$(PYTHON_CMD) -m black .

test: $(DEPS)  ## Run tests
	$(PYTHON_CMD) -m pytest \
		--cov=$(PROJECT) \
		--no-cov-on-fail \
		--cov-fail-under=$(COVERAGE) \
		--cov-report term-missing
