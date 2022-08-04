PYTHON_FILES=$(wildcard *.py) $(wildcard *.pm)
python-style:
	black .
	pylint -f parseable --disable=W,invalid-name,duplicate-code ${PYTHON_FILES}
