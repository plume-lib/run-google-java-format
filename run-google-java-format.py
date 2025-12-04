#!/usr/bin/env python3
"""Reformat each file supplied on the command line.

Yields the Google Java style (by calling out to the google-java-format
program, https://github.com/google/google-java-format), but with
improvements to the formatting of type annotations and annotations in
comments.
"""

import os
import pathlib
import re
import shutil
import stat
import subprocess
import sys
import tempfile
from pathlib import Path
from shutil import copyfileobj

try:
    from urllib import urlopen  # type: ignore[attr-defined]
except ImportError:
    from urllib.request import urlopen

debug = False
# debug = True

script_dir = Path.resolve(Path(__file__)).parent
# Rather than calling out to the shell, it would be better to
# call directly in Python.
fixup_py_name = "fixup-google-java-format.py"
fixup_py_path = script_dir / fixup_py_name

# java_version_string is either 1.8 or nothing.
# For JDK  8, `java -version` has the form: openjdk version "1.8.0_292"
# For JDK 11, `java -version` has the form: openjdk 11.0.11 2021-04-20
# For JDK 17, `java -version` has the form: java 17 2021-09-14 LTS
java_version_string = subprocess.check_output(
    ["java", "-version"], stderr=subprocess.STDOUT
).decode("utf-8")
if debug:
    print("java_version_string =", java_version_string)
match = re.search(r'"(\d+(\.\d+)?).*"', java_version_string)
if not match:
    msg = f'no match for java version string "{java_version_string}"'
    raise Exception(msg)
java_version = match.groups()[0]

## To use an officially released version.
## (Releases appear at https://github.com/google/google-java-format/releases/ ,
## but I keep this in sync with Spotless.)
# Because formatting is inconsistent between versions of GJF, you should
# enable formatting only on versions of Java that support your version of GJF.
# For example, don't format under Java 8/11 if you also use a later version of Java.
# Version 1.3 and earlier do not wrap line comments.
# Version 1.8 and later require JDK 11.
# Version 1.10.0 and later can run under JDK 16.
# Version 1.25.0 and later require JDK 17.
## To set this variable:
## See https://github.com/diffplug/spotless/blob/main/lib/src/main/java/com/diffplug/spotless/java/GoogleJavaFormatStep.java#L75
## or search for "Bump default google" in https://github.com/diffplug/spotless/blob/main/plugin-gradle/CHANGES.md
if java_version == "1.8":
    gjf_version_default = "1.7"
elif java_version == "11":
    gjf_version_default = "1.24.0"
else:
    gjf_version_default = "1.28.0"
gjf_version = os.getenv("GJF_VERSION", gjf_version_default)
gjf_download_prefix = "v" if re.match(r"^1\.[1-9][0-9]", gjf_version) else "google-java-format-"
gjf_snapshot = os.getenv("GJF_SNAPSHOT", "")
gjf_url_base = os.getenv(
    "GJF_URL_BASE",
    "https://github.com/google/google-java-format/releases/download/"
    + gjf_download_prefix
    + gjf_version
    + "/",
)
## To use a non-official version by default, because an official version is
## unusably buggy (like 1.1) or no new release has been made in a long time.
## Never change the file at a URL; make it unique by adding a date.
# gjf_version = "1.5"
# gjf_snapshot = "-SNAPSHOT-20171012"
# gjf_url_base = "http://types.cs.washington.edu/"
# gjf_url_base = "http://homes.cs.washington.edu/~mernst/tmp2/"

gjf_jar_name = "google-java-format-" + gjf_version + gjf_snapshot + "-all-deps.jar"
gjf_url = gjf_url_base + gjf_jar_name


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
    """Like urllib.urlretrieve."""
    with urlopen(url) as in_stream, pathlib.Path(filename).open("wb") as out_file:
        copyfileobj(in_stream, out_file)


# Set gjf_jar_path, or retrieve it if it doesn't appear locally. Does not update
# from remove path if remote is newer, so never change files on the server.
candidate1 = script_dir / gjf_jar_name
candidate2 = script_dir.parent / "lib" / gjf_jar_name
if candidate1.is_file():
    gjf_jar_path = candidate1
elif candidate2.is_file():
    gjf_jar_path = candidate2
else:
    gjf_jar_path = candidate1
    # print("retrieving " + gjf_url + " to " + gjf_jar_path)
    try:
        # Download to a temporary file, then rename atomically.
        # This avoids race conditions with other run-google-java-format processes.
        # "delete=False" because the file will be renamed.
        with tempfile.NamedTemporaryFile(dir=script_dir, delete=False) as f:
            urlretrieve(gjf_url, Path(f.name))
            pathlib.Path(f.name).rename(gjf_jar_path)
    except Exception as e:
        raise Exception("Problem while retrieving " + gjf_url + " to " + str(gjf_jar_path)) from e


# Don't replace local with remote if local is under version control.
# It would be better to just test whether the remote is newer than local,
# but raw GitHub URLs don't have the necessary last-modified information.
if not under_git(script_dir, fixup_py_name):
    url = (
        "https://raw.githubusercontent.com/plume-lib/run-google-java-format/master/" + fixup_py_name
    )
    try:
        urlretrieve(url, fixup_py_path)
    except Exception:
        if pathlib.Path(fixup_py_path).exists():
            print("Couldn't retrieve " + fixup_py_name + " from " + url + "; using cached version")
        else:
            print("Couldn't retrieve " + fixup_py_name + " from " + url)
            sys.exit(1)
    fixup_py_path.chmod(fixup_py_path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

if debug:
    print("script_dir:", script_dir)
    print("fixup_py_path: ", fixup_py_path)
    print("gjf_jar_path: ", gjf_jar_path)

files = sys.argv[1:]
if len(files) == 0:
    print("run-google-java-format.py expects 1 or more filenames as arguments")
    sys.exit(1)

if java_version == "1.8":
    jdk_opens = []
else:
    # From https://github.com/google/google-java-format/releases/
    # This is no longer required as of GJF version 1.15.0, but users might
    # supply a version number lower than that.
    jdk_opens = [
        "--add-exports",
        "jdk.compiler/com.sun.tools.javac.api=ALL-UNNAMED",
        "--add-exports",
        "jdk.compiler/com.sun.tools.javac.file=ALL-UNNAMED",
        "--add-exports",
        "jdk.compiler/com.sun.tools.javac.parser=ALL-UNNAMED",
        "--add-exports",
        "jdk.compiler/com.sun.tools.javac.tree=ALL-UNNAMED",
        "--add-exports",
        "jdk.compiler/com.sun.tools.javac.util=ALL-UNNAMED",
    ]

result = subprocess.call(["java", *jdk_opens, "-jar", str(gjf_jar_path), "--replace", *files])

## This if statement used to be commented out, because google-java-format
## crashed a lot.  It seems more stable now.
# Don't stop if there was an error, because google-java-format won't munge
# files and we still want to run fixup-google-java-format.py.
if result != 0:
    print("Error", result, "when running google-java-format")
    sys.exit(result)

# Remove command-line arguments
files = [f for f in files if not f.startswith("-")]
# Exit if no files were supplied (maybe "--help" was supplied)
if not files:
    sys.exit(0)

if debug:
    print("Running " + fixup_py_name)
result = subprocess.call([fixup_py_path, *files])
if result != 0:
    print("Error", result, "when running " + fixup_py_name)
    sys.exit(result)
