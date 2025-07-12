style-fix: python-style-fix
style-check: python-style-check python-typecheck

PYTHON_FILES:=$(wildcard *.py)
install-mypy:
	@if ! command -v mypy ; then pip install mypy ; fi
install-ruff:
	@if ! command -v ruff ; then pipx install ruff ; fi
python-style-fix: install-ruff
	@ruff format ${PYTHON_FILES}
	@ruff -q check ${PYTHON_FILES} --fix
python-style-check: install-ruff
	@ruff -q format --check ${PYTHON_FILES}
	@ruff -q check ${PYTHON_FILES}
python-typecheck: install-mypy
	@mypy --strict --install-types --non-interactive ${PYTHON_FILES} > /dev/null 2>&1 || true
	mypy --strict --ignore-missing-imports ${PYTHON_FILES}
