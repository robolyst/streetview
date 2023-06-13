ifneq (,$(wildcard ./.env))
    include .env
    export
endif

SHELL := $(shell which bash)
MICROMAMBA := $(PWD)/.micromamba
MAMBA := $(MICROMAMBA)/micromamba
VENV := $(PWD)/.venv
DEPS := $(VENV)/.deps
PROJECT := streetview
PROJECT_DIR = $(PWD)/$(PROJECT)
TEST_DIR = $(PWD)/tests
PYTHON_VERSION ?= 3.11
PYTHON_CMD := PYTHONPATH=$(PWD) $(VENV)/bin/python
COVERAGE := 90  # Required code coverage

ifndef VERBOSE
.SILENT:
endif

.PHONY: help deps python clean check format test build

help:
	grep -E '[0-9a-zA-Z_-]+:.*?## .*$$' Makefile | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

$(MAMBA):
	echo "Installing Mamba..."
	$(SHELL) ./install-micromamba.sh "$(MICROMAMBA)"

$(DEPS): environment.yml $(MAMBA)
	echo "Installing dependencies..."
	rm -rf $(VENV)
	$(MAMBA) create --quiet --yes -p $(VENV)
	$(MAMBA) install --quiet --yes --log-level 4 -p $(VENV) python=$(PYTHON_VERSION) -c conda-forge
	$(MAMBA) install --quiet --yes --log-level 4 -p $(VENV) -f environment.yml
	cp environment.yml $(DEPS)


deps: $(DEPS)  ## Install project dependencies

python: $(DEPS)  ## Drop into a Python REPL
	$(PYTHON_CMD)

clean:  ## Delete unnecessary files from the project
	rm -rf $(MICROMAMBA)
	rm -rf $(VENV)
	rm -rf output.txt
	rm -rf .pytest_cache
	rm -rf .coverage
	rm -rf .mypy_cache
	rm -rf dist
	rm -rf streetview.egg-info
	find . -name __pycache__ | xargs rm -rf

check: $(DEPS)  ## Code style checks (isort, flake8 and mypy)
	- $(PYTHON_CMD) -m isort . --diff
	- $(PYTHON_CMD) -m flake8 $(PROJECT_DIR) $(TEST_DIR)
	- $(PYTHON_CMD) -m black . --diff
	- $(PYTHON_CMD) -m mypy -p $(PROJECT)

format: $(DEPS)  ## Run auto linting
	$(PYTHON_CMD) -m isort .
	$(PYTHON_CMD) -m black .

test: $(DEPS)  ## Run tests
	- $(PYTHON_CMD) -m pytest \
		--cov=$(PROJECT) \
		--no-cov-on-fail \
		--cov-fail-under=$(COVERAGE) \
		--cov-report term-missing

build: $(DEPS)  ## Build the package
	$(PYTHON_CMD) -m build
	$(PYTHON_CMD) -m twine check --strict dist/*