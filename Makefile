.PHONY: all

all: style-fix style-check

type-qualifiers.txt:
	grep --recursive --files-with-matches -e '^@Target\b.*TYPE_USE' ${CHECKERFRAMEWORK}/checker/src/test ${CHECKERFRAMEWORK}/checker-qual/src/main/java ${CHECKERFRAMEWORK}/framework/src/main/java ${CHECKERFRAMEWORK}/docs/examples/units-extension ${CHECKERFRAMEWORK}/framework/src/test/java \
	| grep -v '~' | sed 's:.*/::' \
	| awk '{print $$1} END {print "NotNull.java"; print "UbTop.java"; print "LbTop.java"; print "UB_TOP.java"; print "LB_TOP.java";}' \
	| sed 's/\(.*\)\.java/    "\1",/' \
	| LC_COLLATE=C sort | uniq > $@

.PHONY: tags
TAGS: tags
tags:
	etags *.py

# Code style
ifeq (,$(wildcard .plume-scripts))
dummy != git clone -q https://github.com/plume-lib/plume-scripts.git .plume-scripts
endif
include .plume-scripts/code-style.mak
