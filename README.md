# run-google-java-format

Scripts to automatically download and run google-java-format,
and to slightly improve its output.

## run-google-java-format.py

The [google-java-format](https://github.com/google/google-java-format)
program reformats Java source code, but it creates poor formatting for
annotations in comments.  This script runs google-java-format and then
performs small changes to improve formatting of annotations in comments.
If called with no arguments, it reads from and writes to standard output.

[Documentation](https://raw.githubusercontent.com/plume-lib/run-google-java-format/master/run-google-java-format.py)
at top of file.

## check-google-java-format.py</dt>

Given `.java` file names on the command line, reports any that
would be reformatted by the run-google-java-format.py program, and returns
non-zero status if there were any.
If called with no arguments, it reads from standard output.

[Documentation](https://raw.githubusercontent.com/mernst/plume-lib/master/bin/check-google-java-format.py)
at top of file.
