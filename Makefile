
default: test

.req.%: %-requirements.txt
	pip install -Ur $<
	@ touch $@

test: .req.test
	pytest
