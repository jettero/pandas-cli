
default: check-all-and-build

check-all-and-build:
	@+ make --no-print-directory pre-commit
	@+ make --no-print-directory test
	@+ make --no-print-directory build
	@+ make --no-print-directory test-feed-json

pre-commit: .req.dev
	pre-commit run -a

test-feed-%: pandas_cli/version.py .req.test
	./test/bin/gen_$*.py | ./pd -f csv

test/output/1.%: test/conftest .req.test
	pytest --setup-only

test: .req.test
	pytest

v version pandas_cli/version.py: .req.dev
	python -m setuptools_scm

build: .req.dev
	python -m build

.req.pipup:
	pip install -U pip
	pip install -U wheel
	@ touch $@

.req: requirements.txt .req.pipup
	pip install -Ur $<
	@ touch $@

.req.%: %-requirements.txt .req.pipup
	pip install -Ur $<
	@ touch $@
