PYTHON_FILES=$(wildcard *.py) $(wildcard *.pm)
python-style:
	yapf3 -i --style='{column_limit: 100}' ${PYTHON_FILES}
	pylint -f parseable --disable=W,invalid-name,duplicate-code ${PYTHON_FILES}
