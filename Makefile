style-fix: python-style-fix
style-check: python-style-check python-typecheck

PYTHON_FILES:=$(wildcard *.py)
python-style-fix:
	@ruff format ${PYTHON_FILES}
	@ruff -q check ${PYTHON_FILES} --fix
python-style-check:
	@ruff -q format --check ${PYTHON_FILES}
	@ruff -q check ${PYTHON_FILES}
python-typecheck:
	@mypy --strict --install-types --non-interactive ${PYTHON_FILES} > /dev/null 2>&1 || true
	mypy --strict --ignore-missing-imports ${PYTHON_FILES}
