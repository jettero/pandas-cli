# NOTE: makefile completely optional, just a list of aliases

test: .reqs
	pytest

praf pre-commit-all-files: .reqs
	pre-commit run --all-files

build:
	python -m build

.reqs: requirements.txt test-requirements.txt
	@touch $@
	pip install -Ur requirements.txt -r test-requirements.txt

requirements.txt: .base-reqs
	toml-to-req --toml-file pyproject.toml --requirements-file $@

test-requirements.txt: .base-reqs
	toml-to-req --toml-file pyproject.toml --optional-lists test --requirements-file $@

.base-reqs:
	@touch $@
	pip install -U pip setuptools wheel toml-to-requirements
