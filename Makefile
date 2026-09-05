.PHONY: check lint type test

check: lint type test

lint:
	ruff check .

type:
	mypy src tests

test:
	pytest --cov=study_os_benchmarker --cov-branch --cov-report=term-missing
