#!/usr/bin/env python3
"""
This script reformats each file supplied on the command line according to
the Google Java style (by calling out to the google-java-format program,
https://github.com/google/google-java-format), but with improvements to
the formatting of annotations in comments.
"""

from __future__ import print_function
import filecmp
import os
import re
import stat
import shutil
import subprocess
import sys
import tempfile

from shutil import copyfileobj

try:
    from urllib import urlopen
except ImportError:
    from urllib.request import urlopen

debug = False
# debug = True

script_dir = os.path.dirname(os.path.abspath(__file__))
# Rather than calling out to the shell, it would be better to
# call directly in Python.
fixup_py = os.path.join(script_dir, "fixup-google-java-format.py")

# java_version_string is either 1.8 or nothing.
# For JDK  8, `java -version` has the form: openjdk version "1.8.0_292"
# For JDK 11, `java -version` has the form: openjdk 11.0.11 2021-04-20
# For JDK 17, `java -version` has the form: java 17 2021-09-14 LTS
java_version_string = subprocess.check_output(
    ["java", "-version"], stderr=subprocess.STDOUT
).decode("utf-8")
if debug:
    print("java_version_string =", java_version_string)
java_version = re.search('"(\d+(\.\d+)?).*"', java_version_string).groups()[0]

## To use an officially released version.
## (Releases appear at https://github.com/google/google-java-format/releases/ ,
## but I keep this in sync with Spotless.)
# Version 1.8 and later require JDK 11 to run, and it reflows string literals.
# Note that due to changes since GJF 1.7, formatting with GJF 1.7 is
# inconsistent with later versions of GJF, so you should probably disable
# formatting on Java 8 if you also use a later version of Java.
# Version 1.10.0 and later can run under JDK 16.
## To set this variable:
## See https://github.com/diffplug/spotless/blob/main/lib/src/main/java/com/diffplug/spotless/java/GoogleJavaFormatStep.java#L75
## or search for "Bump default google" in https://github.com/diffplug/spotless/blob/main/plugin-gradle/CHANGES.md
gjf_version_default = "1.7" if (java_version == "1.8") else "1.17.0"
gjf_version = os.getenv("GJF_VERSION", gjf_version_default)
gjf_download_prefix = (
    "v" if re.match(r"^1\.1[0-9]", gjf_version) else "google-java-format-"
)
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


def urlretrieve(url, filename):
    """Like urllib.urlretrieve."""
    with urlopen(url) as in_stream, open(filename, "wb") as out_file:
        copyfileobj(in_stream, out_file)


# Set gjf_jar_path, or retrieve it if it doesn't appear locally. Does not update
# from remove path if remote is newer, so never change files on the server.
if os.path.isfile(os.path.join(script_dir, gjf_jar_name)):
    gjf_jar_path = os.path.join(script_dir, gjf_jar_name)
elif os.path.isfile(os.path.join(os.path.dirname(script_dir), "lib", gjf_jar_name)):
    gjf_jar_path = os.path.join(os.path.dirname(script_dir), "lib", gjf_jar_name)
else:
    gjf_jar_path = os.path.join(script_dir, gjf_jar_name)
    # print("retrieving " + gjf_url + " to " + gjf_jar_path)
    try:
        # Download to a temporary file, then rename atomically.
        # This avoids race conditions with other run-google-java-format processes.
        # "delete=False" because the file will be renamed.
        with tempfile.NamedTemporaryFile(dir=script_dir, delete=False) as f:
            urlretrieve(gjf_url, f.name)
            os.rename(f.name, gjf_jar_path)
    except:
        print("Problem while retrieving " + gjf_url + " to " + gjf_jar_path)
        raise


# For some reason, the "git ls-files" must be run from the root.
# (I can run "git ls-files" from the command line in any directory.)
def under_git(dir, filename):
    """Return true if filename in dir is under git control."""
    if not shutil.which("git"):
        if debug:
            print("no git executable found")
        return False
    with subprocess.Popen(
        ["git", "ls-files", filename, "--error-unmatch"],
        cwd=dir,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.STDOUT,
    ) as p:
        p.wait()
        if debug:
            print("p.returncode", p.returncode)
        return p.returncode == 0


# Don't replace local with remote if local is under version control.
# It would be better to just test whether the remote is newer than local,
# but raw GitHub URLs don't have the necessary last-modified information.
if not under_git(script_dir, "fixup-google-java-format.py"):
    try:
        urlretrieve(
            "https://raw.githubusercontent.com/"
            + "plume-lib/run-google-java-format/master/fixup-google-java-format.py",
            fixup_py,
        )
    except:
        if os.path.exists(fixup_py):
            print("Couldn't retrieve fixup-google-java-format.py; using cached version")
        else:
            print("Couldn't retrieve fixup-google-java-format.py")
            sys.exit(1)
    os.chmod(
        fixup_py, os.stat(fixup_py).st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH
    )

if debug:
    print("script_dir:", script_dir)
    print("fixup_py: ", fixup_py)
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

result = subprocess.call(
    ["java"] + jdk_opens + ["-jar", gjf_jar_path, "--replace"] + files
)

## This if statement used to be commented out, because google-java-format
## crashed a lot.  It seems more stable now.
# Don't stop if there was an error, because google-java-format won't munge
# files and we still want to run fixup-google-java-format.py.
if result != 0:
    print("Error when running google-java-format")
    sys.exit(result)

# Remove command-line arguments
files = [f for f in files if not f.startswith("-")]
# Exit if no files were supplied (maybe "--help" was supplied)
if not files:
    sys.exit(0)

if debug:
    print("Running fixup-google-java-format.py")
result = subprocess.call([fixup_py] + files)
if result != 0:
    print("Error when running fixup-google-java-format.py")
    sys.exit(result)
