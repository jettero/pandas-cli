# NOTE: makefile completely optional, just a list of aliases

test: .reqs
	pytest

build: .reqs
	python -m build

praf pre-commit-all-files: .reqs
	pre-commit run --all-files

.reqs: requirements.txt test-requirements.txt
	@touch $@
	pip install -Ur requirements.txt -r test-requirements.txt

requirements.txt: pyproject.toml .base-reqs
	toml-to-req --toml-file $< --requirements-file $@

test-requirements.txt: pyproject.toml .base-reqs
	toml-to-req --toml-file $< --optional-lists test --requirements-file $@

.base-reqs:
	@touch $@
	pip install -U pip setuptools wheel toml-to-requirements
