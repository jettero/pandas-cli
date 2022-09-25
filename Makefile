
default: test

test: .req.test
	pytest

build: .req
	python -m build

.req.pipup:
	pip install -U pip
	pip install -U wheel
	@ touch $@

.req.build: .req.pipup
	pip install -U build
	@ touch $@

.req: requirements.txt .req.build
	pip install -Ur $<
	@ touch $@

.req.%: %-requirements.txt .req.pipup
	pip install -Ur $<
	@ touch $@
