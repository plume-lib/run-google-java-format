PYTHON_FILES=$(wildcard *.py) $(wildcard *.pm)
python-style:
	ruff format ${PYTHON_FILES}
	ruff check ${PYTHON_FILES} --fix
