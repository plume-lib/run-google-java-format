all: style-fix style-check

type-qualifiers.txt:
	grep --recursive --files-with-matches -e '^@Target\b.*TYPE_USE' ${CHECKERFRAMEWORK}/checker/src/test ${CHECKERFRAMEWORK}/checker-qual/src/main/java ${CHECKERFRAMEWORK}/framework/src/main/java ${CHECKERFRAMEWORK}/docs/examples/units-extension ${CHECKERFRAMEWORK}/framework/src/test/java \
	| grep -v '~' | sed 's:.*/::' \
	| awk '{print $$1} END {print "NotNull.java"; print "UbTop.java"; print "LbTop.java"; print "UB_TOP.java"; print "LB_TOP.java";}' \
	| sed 's/\(.*\)\.java/    "\1",/' \
	| LC_COLLATE=C sort | uniq > $@

TAGS: tags
tags:
	etags *.py

### Code style

style-fix: python-style-fix
style-check: python-style-check python-typecheck
PYTHON_FILES:=$(wildcard **/*.py) $(shell grep -r -l --exclude-dir=.git --exclude-dir=.venv --exclude='*.py' --exclude='#*' --exclude='*~' --exclude='*.tar' --exclude=gradlew --exclude=lcb_runner '^\#! \?\(/bin/\|/usr/bin/\|/usr/bin/env \)python')
python-style-fix:
ifneq (${PYTHON_FILES},)
#	@uvx ruff --version
	@uvx ruff format ${PYTHON_FILES}
	@uvx ruff -q check ${PYTHON_FILES} --fix
endif
python-style-check:
ifneq (${PYTHON_FILES},)
#	@uvx ruff --version
	@uvx ruff -q format --check ${PYTHON_FILES}
	@uvx ruff -q check ${PYTHON_FILES}
endif
python-typecheck:
ifneq (${PYTHON_FILES},)
	@uv run ty check
endif
showvars::
	@echo "PYTHON_FILES=${PYTHON_FILES}"
