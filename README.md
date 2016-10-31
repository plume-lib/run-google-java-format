# run-google-java-format

Scripts to automatically download and run google-java-format,
and to slightly improve its output.

The [google-java-format](https://github.com/google/google-java-format)
program reformats Java source code, but has some disadvantages:
 * It's inconvenient to install.
 * To reformat code, it requires a long, hard-to-remember command line.
 * It cannot check whether a file is properly formatted, which is desirable in a pre-commit hook.
 * It creates poor formatting for [annotations in comments](https://types.cs.washington.edu/checker-framework/current/checker-framework-manual.html#annotations-in-comments).

The `run-google-java-format.py` and `check-google-java-format.py` scripts correct these problems.


## run-google-java-format.py

This script reformats each file supplied on the command line according to
the Google Java style, but with improvements to the formatting of
annotations in comments.
If called with no arguments, it reads from and writes to standard output.


## check-google-java-format.py</dt>

Given `.java` file names on the command line, reports any that would be
reformatted by the `run-google-java-format.py` program, and returns
non-zero status if there were any.
If called with no arguments, it reads from standard output.
You could invoke this program, for example, in a git pre-commit hook (see below).


## Installing

There are two ways to install and use these scripts:
 * clone the repository (run `git clone
   https://github.com/plume-lib/run-google-java-format.git`) and run the
   scripts from there
 * download the
   [run-google-java-format.py](https://raw.githubusercontent.com/plume-lib/run-google-java-format/master/run-google-java-format.py)
   or
   [check-google-java-format.py](https://raw.githubusercontent.com/plume-lib/run-google-java-format/master/check-google-java-format.py)
   file and run it.  The file will automatically download any additional
   needed files.


## Integrating with a build system

Add the following targets to your build system.

Integration with other build systems is similar.  (Feel free to contribute
concrete exmaples for build systems that are not listed here.)


### Makefile

```
JAVA_FILES_TO_FORMAT ?= $(shell find src -name '*.java' -print | grep -v '\.\#' | grep -v WeakHasherMap.java | grep -v WeakIdentityHashMap.java | grep -v MathMDE.java | sort)

get-run-google-java-format:
	@-git -C .run-google-java-format pull -q || git clone -q https://github.com/plume-lib/run-google-java-format.git .run-google-java-format

reformat:
	${MAKE) get-run-google-java-format
	@./.run-google-java-format/run-google-java-format.py ${JAVA_FILES_TO_FORMAT}

check-format:
	${MAKE) get-run-google-java-format
	@./.run-google-java-format/check-google-java-format.py ${JAVA_FILES_TO_FORMAT}
```

To output a message when there are malformatted files,
you could add ` || (echo "Try running:  make reformat" && false)`
at the end of the last line of the `check-format` target.


### Ant `build.xml`

```
  <fileset id="formatted.java.files" dir="." includes="**/*.java" excludes="**/checker/jdk/,**/stubparser/,**/eclipse/,**/nullness-javac-errors/"/>

  <target name="-get-run-google-java-format"
          description="Obtain or update run-google-java-format project">
    <exec executable="/bin/sh">
      <arg value="-c"/>
      <arg value="git -C .run-google-java-format pull -q || git clone -q https://github.com/plume-lib/run-google-java-format.git .run-google-java-format"/>
    </exec>
  </target>

  <target name="reformat" depends="-get-run-google-java-format"
          description="Reformat Java code">
    <apply executable="python" failonerror="true">
      <arg value="./.run-google-java-format/run-google-java-format.py"/>
      <fileset refid="formatted.java.files"/>
    </apply>
  </target>

  <target name="check-format" depends="-get-run-google-java-format"
          description="Check Java code formatting">
    <apply executable="python" failonerror="true">
      <arg value="./.run-google-java-format/check-google-java-format.py"/>
      <fileset refid="formatted.java.files"/>
    </apply>
  </target>
```



### Git pre-commit hook

Here is an example of what you might put in a Git pre-commit hook:
(For efficiency, this only checks the files that are being comitted.)

```
CHANGED_JAVA_FILES=`git diff --staged --name-only --diff-filter=ACM | grep '\.java$'` || true
if [ ! -z "$CHANGED_JAVA_FILES" ]; then
    git -C .run-google-java-format pull -q || git clone -q https://github.com/plume-lib/run-google-java-format.git .run-google-java-format
    ./.run-google-java-format/check-google-java-format.py ${CHANGED_JAVA_FILES}
fi
```

You will also want to add `.run-google-java-format` to your
`~/.gitignore-global` file or your project's `.gitignore` file.


#### Finding trailing spaces

Not related to google-java-format, here is code for your Git pre-commit
hook that finds files that have trailing spaces:  (google-java-format will complain about Java files with trailing spaces, but this is useful for other types of files.)

```
CHANGED_STYLE_FILES=`git diff --staged --name-only --diff-filter=ACM` || true
if [ ! -z "$CHANGED_STYLE_FILES" ]; then
    FILES_WITH_TRAILING_SPACES=`grep -l -s '[[:blank:]]$' ${CHANGED_STYLE_FILES} 2>&1` || true
    if [ ! -z "$FILES_WITH_TRAILING_SPACES" ]; then
        echo "Some files have trailing whitespace: ${FILES_WITH_TRAILING_SPACES}" && exit 1
    fi
fi
```


## Dealing with large changes when reformatting your codebase

When you first apply standard formatting, that may be disruptive to people
who have changes in their own branches/clones/forks.
(But, once you settle on consistent formatting, you will enjoy a number of
benefits.  Applying standard formatting to your codebase makes it easier to
read.  It also simplifies use of a version control system:  it reduces the
likelihood of merge conflicts due to formatting changes, and it ensures
that commits and pull requests don't intermingle substantive changes with
formatting changes.)

Here are some notes about a possible way to deal with upstream
reformatting.  Comments/improvements are welcome.

For the person doing the reformatting:

 * Create a new branch and do your work there.
   ```git checkout -b reformat-gjf```
 * Tag the commit before the whitespace change as "before reformatting".
   ```git tag -a before-reformatting -m "Code before running google-java-format"```
 * Reformat by running a command such as
   `make reformat`,
   `ant reformat`, or
   `gradle googleJavaFormat` (or whatever buildfile target you have set up).
 * Examine the diffs to look for poor reformatting:

   ```git diff -w -b | grep -v '^[-+]import' | grep -v '^[-+]$'```

   (You may wish to `grep -v` some additional lines, depending on your project.)

   A key example of poor reformatting is when you have a single statement
   that is the body of an `if`/`for`/`while` statement.  google-java-format
   will move this onto the previous line with the boolean expression.  It's
   better to use curly braces `{}` on every `then` clause, `else` clause,
   and `for`/`while` body.  To find the poor reformatting:

    * Search for occurrences of `^\+.*\) return `.
    * Search for occurrences of `^\+.*\(if\|while\|for\) (.*) [^{]`.
    * Search for hunks that have fewer `+` than `-` lines.

   Add curly braces to get the body back on its own line.
   (You might want to do this in the master branch, and then start over with adding formatting.)
 * Run tests
 * Commit changes:

   ```git commit -m "Reformat code using google-java-format"```

 * Tag the commit that does the whitespace change as "after reformatting".

   ```git tag -a after-reformatting -m "Code after running google-java-format"```

 * Push both the commits and the tags:

   ```git push --tags```

For a client to merge the massive upstream changes:
Assuming before-reformatting is the last commit before reformatting
and after-reformatting is the reformatting commit:

 * Merge in the commit before the reformatting into your branch.

     ```git merge before-reformatting```

   Or, if you have "myremote" configured as a remote, run these commands:

     ```
     git fetch myremote after-reformatting:after-reformatting
     git fetch myremote before-reformatting:before-reformatting
     ```

 * Resolve any conflicts, run tests, and commit your changes.
 * Merge in the reformatting commit, preferring all your own changes.

     ```git merge after-reformatting -s recursive -X ours```

 * Run `ant reformat` or the equivalent command.
 * Commit any formatting changes.
 * Verify that this contains only changes you made (that is, the formatting
   changes were ignored):

     ```git diff after-reformatting...HEAD```

For a client of a client (such as a fork of a fork), the above instructions must be revised.