#!/usr/bin/env python3

"""A wrapper around the google-java-format program, with improvements.

This script checks whether the files supplied on the command line conform
to the Google Java style (as enforced by the google-java-format program,
but with improvements to the formatting of annotations in comments).
If any files would be affected by running run-google-java-format.py,
this script prints their names and returns a non-zero status.
If called with no arguments, it reads from standard input.
You could invoke this program, for example, in a git pre-commit hook.
"""

# TODO: Thanks to https://github.com/google/google-java-format/pull/106
# this script can be eliminated, or its interface simplified.

import filecmp
import itertools
import os
import shutil
import stat
import subprocess
import sys
import tempfile
from pathlib import Path

try:
    from urllib import urlopen  # ty: ignore[unresolved-import]
except ImportError:
    from urllib.request import urlopen

debug = False
# debug = True

script_dir = Path(__file__).resolve().parent
run_py_name = "run-google-java-format.py"
run_py_path = script_dir / run_py_name


# For some reason, the "git ls-files" must be run from the root.
# (I can run "git ls-files" from the command line in any directory.)
def under_git(directory: Path, filename: str) -> bool:
    """Return true if `filename` in `directory` is under git control.

    Args:
        directory: the directory
        filename: the file name

    Returns:
        true if `filename` in `directory` is under git control.
    """
    if not shutil.which("git"):
        if debug:
            print("no git executable found")
        return False
    with subprocess.Popen(
        ["git", "ls-files", filename, "--error-unmatch"],
        cwd=directory,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.STDOUT,
    ) as p:
        p.wait()
        if debug:
            print("p.returncode", p.returncode)
        return p.returncode == 0


def urlretrieve(url: str, filename: Path) -> None:
    """Like urllib.urlretrieve, but writes `filename` atomically.

    Downloads to a temporary file in the destination directory, then renames it
    into place, so an interrupted transfer never leaves a partial file at
    `filename`.
    """
    with tempfile.NamedTemporaryFile(dir=filename.parent, delete=False) as tmp:
        tmp_path = Path(tmp.name)
        try:
            with urlopen(url) as in_stream:
                shutil.copyfileobj(in_stream, tmp)
        except BaseException:
            tmp_path.unlink(missing_ok=True)
            raise
    # NamedTemporaryFile creates the file mode 0600; instead give it the
    # umask-respecting permissions that a normally-created file would have.
    umask = os.umask(0o022)
    os.umask(umask)
    tmp_path.chmod(0o666 & ~umask)
    tmp_path.rename(filename)


# Don't replace local with remote if local is under version control.
# It would be better to just test whether the remote is newer than local,
# but raw GitHub URLs don't have the necessary last-modified information.
if not under_git(script_dir, run_py_name):
    url = "https://raw.githubusercontent.com/plume-lib/run-google-java-format/master/" + run_py_name
    try:
        urlretrieve(url, run_py_path)
    except Exception:  # ruff:ignore[blind-except]
        if run_py_path.exists():
            print("Couldn't retrieve " + run_py_name + " from " + url + "; using cached version")
        else:
            print("Couldn't retrieve " + run_py_name + " from " + url)
            sys.exit(1)
    run_py_path.chmod(run_py_path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

temp_dir = tempfile.mkdtemp(prefix="check-google-java-format-")
_temp_counter = itertools.count()


def temporary_file_name() -> str:
    """Return the name of a temporary file, unique within this run's temp_dir.

    Returns:
        the name of a temporary file.
    """
    return str(Path(temp_dir) / f"tmp{next(_temp_counter)}")


def cleanup() -> None:
    """Clean up temporary files."""
    shutil.rmtree(temp_dir)


files = sys.argv[1:]
if len(files) == 0:
    content = sys.stdin.read()
    fname = temporary_file_name() + ".java"
    # Write verbatim; appending a newline (as `print` would) would make the
    # comparison below always report improper formatting.
    Path(fname).write_text(content)
    files = [fname]

temps = []
cmdlineargs = [f for f in files if f.startswith("-")]
files = [f for f in files if not f.startswith("-")]
for fname in files:
    ftemp = temporary_file_name() + "_" + Path(fname).name
    shutil.copyfile(fname, ftemp)
    temps.append(ftemp)

if debug:
    print("Running " + run_py_name)
# Problem:  if a file is syntactically illegal, this outputs the temporary file
# name rather than the real file name.
# Minor optimization: To save one process creation, could call directly in Python.
result = subprocess.call([run_py_path, *cmdlineargs, *temps])
if result != 0:
    cleanup()
    sys.exit(result)

exit_code = 0

for file, temp in zip(files, temps, strict=True):
    if not filecmp.cmp(file, temp, shallow=False):
        # TODO: gives temporary file name if reading from stdin
        print("Improper formatting:", file)
        exit_code = 1

cleanup()

sys.exit(exit_code)
