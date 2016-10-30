#!/usr/bin/python

# This script checks whether the files supplied on the command line conform
# to the Google Java style (as enforced by the google-java-format program,
# but with improvements to the formatting of annotations in comments).
# If any files would be affected by running run-google-java-format.py,
# this script prints their names and returns a non-zero status.
# If called with no arguments, it reads from standard input.
# You could invoke this program, for example, in a git pre-commit hook.

# Here are example targets you might put in a Makefile; integration with
# other build systems is similar.
#
# reformat:
# 	@wget -N https://raw.githubusercontent.com/plume-lib/run-google-java-format/master/run-google-java-format.py
# 	@run-google-java-format.py ${JAVA_FILES_FOR_FORMAT}
#
# check-format:
# 	@wget -N https://raw.githubusercontent.com/plume-lib/run-google-java-format/master/check-google-java-format.py
# 	@check-google-java-format.py ${JAVA_FILES_FOR_FORMAT} || (echo "Try running:  make reformat" && false)

# Here is an example of what you might put in a Git pre-commit hook.
#
# CHANGED_JAVA_FILES=`git diff --staged --name-only --diff-filter=ACM | grep '\.java$'` || true
# if [ ! -z "$CHANGED_JAVA_FILES" ]; then
#     wget -N https://raw.githubusercontent.com/plume-lib/run-google-java-format/master/check-google-java-format.py
#     python check-google-java-format.py ${CHANGED_JAVA_FILES}
# fi


from __future__ import print_function
from distutils import spawn
import filecmp
import os
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import urllib

debug = False
# debug = True

script_dir = os.path.dirname(os.path.abspath(__file__))
run_py = os.path.join(script_dir, "run-google-java-format.py")

# For some reason, the "git ls-files" must be run from the root.
# (I can run "git ls-files" from the command line in any directory.)
def under_git(dir, filename):
    """Return true if filename in dir is under git control."""
    if not spawn.find_executable("git"):
        if debug:
            print("no git executable found")
        return False
    FNULL = open(os.devnull, 'w')
    p = subprocess.Popen(["git", "ls-files", filename, "--error-unmatch"], cwd=dir, stdout=FNULL, stderr=subprocess.STDOUT)
    p.wait()
    if debug:
        print("p.returncode", p.returncode)
    return p.returncode == 0

# Don't replace local with remote if local is under version control.
# It would be better to just test whether the remote is newer than local,
# But raw GitHub URLs don't have the necessary last-modified information.
if not under_git(script_dir+"/..", "bin/run-google-java-format.py"):
    urllib.urlretrieve("https://raw.githubusercontent.com/plume-lib/run-google-java-format/master/run-google-java-format.py", run_py)
    os.chmod(run_py, os.stat(run_py).st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

temp_dir = tempfile.mkdtemp(prefix='check-google-java-format-')

def temporary_file_name():
    return os.path.join(temp_dir, next(tempfile._get_candidate_names()))

def cleanup():
    shutil.rmtree(temp_dir)


files = sys.argv[1:]
if len(files) == 0:
    content = sys.stdin.read()
    fname = temporary_file_name() + ".java"
    with open(fname,'w') as outfile:
        print(content, file=outfile)
    files = [fname]

temps = []
cmdlineargs = [f for f in files if f.startswith("-")]
files = [f for f in files if not f.startswith("-")]
for fname in files:
    ftemp = temporary_file_name() + ".java"
    shutil.copyfile(fname, ftemp)
    temps.append(ftemp)

if debug: print("Running run-google-java-format.py")
# To save one process creation, could call directly in Python.
result = subprocess.call([run_py] + cmdlineargs + temps)
if result != 0:
    cleanup()
    sys.exit(result)

exit_code = 0

for i in range(len(files)):
    if not filecmp.cmp(files[i], temps[i]):
        # TODO: gives temporary file name if reading from stdin
        print("Improper formatting:", files[i])
        exit_code = 1

cleanup()

sys.exit(exit_code)
