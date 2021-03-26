# run-google-java-format

This repository contains the `run-google-java-format.py` and
`check-google-java-format.py` scripts.
They automatically download and run
[google-java-format](https://github.com/google/google-java-format),
they slightly improve its output, and they add checking functionality.

The [google-java-format](https://github.com/google/google-java-format), or GJF,
program reformats Java source code.  It is a good formatter, but
this project (run-google-java-format) improves it:
 * This project creates better formatting for [type annotations](https://github.com/google/google-java-format/issues/5).
 * This project creates better formatting for [annotations in comments](https://types.cs.washington.edu/checker-framework/current/checker-framework-manual.html#annotations-in-comments).
 * This project can check whether a file is properly formatted, which is desirable in a pre-commit hook.
   (Update: Version 1.5 of GJF can do this, but it is not cognizant of the better formatting that this project does.)
 * This project has a handy script to reformat code; by contrast, GJF requires a long, hard-to-remember command line.
 * You can run this project in a way that automatically uses the latest version of GJF, if you wish, without having to remember to update your GJF installation periodically.  (You can also control which version of GJF this project uses; see "Customization" below.)

The `run-google-java-format.py` and `check-google-java-format.py` scripts provide these enhancements over plain google-java-format.


## run-google-java-format.py

This script reformats each file supplied on the command line according to
the Google Java style, but with improvements to the formatting of
annotations in comments.
If called with no arguments, it reads from and writes to standard output.


## check-google-java-format.py

Given `.java` file names on the command line, reports any that would be
reformatted by the `run-google-java-format.py` program, and returns
non-zero status if there were any.
If called with no arguments, it reads from standard output.
You could invoke this program, for example, in a git pre-commit hook (see below).


## Installing

There are two ways to install and use these scripts:
 * Clone the repository (run `git clone
   https://github.com/plume-lib/run-google-java-format.git`) and run the
   scripts from there.
 * Download the
   [run-google-java-format.py](https://raw.githubusercontent.com/plume-lib/run-google-java-format/master/run-google-java-format.py)
   or
   [check-google-java-format.py](https://raw.githubusercontent.com/plume-lib/run-google-java-format/master/check-google-java-format.py)
   file and run it.  The file will automatically download any additional
   needed files.


## Customization

To control which version of google-java-format to use,
set environment variable `GJF_VERSION`.  For example:

```export GJF_VERSION=1.3```


## Integrating with a build system

Add the following targets to your build system.

Integration with other build systems is similar.  (Feel free to contribute
concrete examples for build systems that are not listed here.)

Some of these commands have only been tested on Unix;
if you can create a version that also works on Windows, please contribute it.


### Makefile

```
JAVA_FILES_TO_FORMAT ?= $(shell find src -name '*.java' -print | grep -v '\.\#' | grep -v WeakHasherMap.java | grep -v WeakIdentityHashMap.java | grep -v MathMDE.java | sort)

update-run-google-java-format:
	@[ -d .run-google-java-format ] && (cd .run-google-java-format && git pull -q) || git clone -q https://github.com/plume-lib/run-google-java-format.git .run-google-java-format

# Requires Java 8
reformat:
	${MAKE} update-run-google-java-format
	@./.run-google-java-format/run-google-java-format.py ${JAVA_FILES_TO_FORMAT}

# Requires Java 8
check-format:
	${MAKE} update-run-google-java-format
	@./.run-google-java-format/check-google-java-format.py ${JAVA_FILES_TO_FORMAT} || (echo "Try running:  make reformat" && /bin/false)
```


### Ant `build.xml`

At the top of your Ant file, augment the `<project>` block:

```
<project ...
         xmlns:if="ant:if" xmlns:unless="ant:unless">
```

Then, add this:

```
  <!-- Adjust for your project. -->
  <fileset id="formatted.java.files" dir="." includes="**/*.java" excludes="**/checker/jdk/,**/stubparser/,**/eclipse/,**/nullness-javac-errors/"/>

  <condition property="isMac">
    <os family="mac" />
  </condition>

  <!-- Avoids "Argument list too long" message.  You can also set
       this property in file local.properties. -->
  <condition property="maxparallel" value="1000" else="-1">
    <isset property="isMac"/>
  </condition>

  <target name="-run-google-java-format.check">
    <condition property="run-google-java-format.exists">
      <available file=".run-google-java-format" type="dir"/>
    </condition>
  </target>

  <target name="-get-run-google-java-format"
          description="Obtain the run-google-java-format project"
          depends="-run-google-java-format.check"
          unless="run-google-java-format.exists">
    <exec executable="git"
          dir=".">
      <arg value="clone"/>
      <arg value="-q"/>
      <arg value="https://github.com/plume-lib/run-google-java-format.git"/>
      <arg value=".run-google-java-format"/>
    </exec>
  </target>

  <target name="update-run-google-java-format"
          description="Update the run-google-java-format project"
          depends="-get-run-google-java-format">
    <exec executable="git"
          dir=".run-google-java-format">
      <arg value="pull"/>
      <arg value="-q"/>
    </exec>
  </target>

  <target name="reformat" depends="update-run-google-java-format"
          description="Reformat Java code">
    <apply executable="python3" parallel="true" maxparallel="${maxparallel}" failonerror="true">
      <arg value="./.run-google-java-format/run-google-java-format.py"/>
      <fileset refid="formatted.java.files"/>
    </apply>
  </target>

  <target name="check-format" depends="update-run-google-java-format"
          description="Check Java code formatting">
    <apply executable="python3" parallel="true" maxparallel="${maxparallel}"
       failonerror="false" resultproperty="check.format.result"
       outputproperty="check.format.stdout" errorproperty="check.format.stderr">
      <arg value="./.run-google-java-format/check-google-java-format.py"/>
      <fileset refid="formatted.java.files"/>
    </apply>
    <echo unless:blank="${check.format.stdout}">${check.format.stdout}</echo>
    <echo unless:blank="${check.format.stderr}">${check.format.stderr}</echo>
    <echo unless:blank="${check.format.stderr}">Fix syntax errors, then re-run:  ant check-format</echo>
    <echo unless:blank="${check.format.stdout}" if:blank="${check.format.stderr}">Try running:  ant reformat</echo>
    <fail>
      <condition>
        <not>
          <equals arg1="0" arg2="${check.format.result}"/>
        </not>
      </condition>
    </fail>
  </target>
```


### Gradle `build.gradle`

Customize per your requirements, such as excluding generated `.java` files from formatting.

```
task getCodeFormatScripts {
  description "Obtain the run-google-java-format scripts"
  doLast {
    def rgjfDir = "$projectDir/.run-google-java-format"
    if (! new File(rgjfDir).exists()) {
      exec {
        commandLine 'git', 'clone', '--depth', '1', "https://github.com/plume-lib/run-google-java-format.git", rgjfDir
      }
    } else {
      // Ignore exit value so this does not halt the build when not connected to the Internet.
      exec {
        workingDir rgjfDir
        ignoreExitValue true
        commandLine 'git', 'pull', '-q'
      }
    }
  }
}

task pythonIsInstalled(type: Exec) {
  description "Check that the python3 executable is installed."
  executable = "python3"
  args "--version"
}

task checkFormat(type: Exec, dependsOn: [getCodeFormatScripts, pythonIsInstalled], group: 'Formatting') {
  description "Check whether the Java source code is properly formatted"
  def javaFiles = fileTree("$projectDir").matching{ include "**/*.java" } as List
  def pythonArgs = javaFiles.clone()
  pythonArgs.add(0, "$projectDir/.run-google-java-format/check-google-java-format.py")

  commandLine "python3"
  args pythonArgs
  ignoreExitValue true

  doLast {
    if (execResult.exitValue != 0) {
      throw new GradleException("Found improper formatting, try running:  ./gradlew reformat")
    }
  }
}

task reformat(type: Exec, dependsOn: [getCodeFormatScripts, pythonIsInstalled], group: 'Formatting') {
  description "Format the Java source code according to the Google Java Format style"
  def javaFiles = fileTree("$projectDir").matching{ include "**/*.java" } as List
  def pythonArgs = javaFiles.clone()
  pythonArgs.add(0, "$projectDir/.run-google-java-format/run-google-java-format.py")

  commandLine "python3"
  args pythonArgs
}
```

<!--
It ought to be possible to replace the `getCodeFormatScripts` task above
with the below, but DO NOT DO SO because in some cases it corrupts your
repository by writing over the top-level .git file rather than creating a
new .git file in directory in the .run-google-java-format directory


plugins {
  id 'org.ajoberstar.grgit' version '2.3.0' apply false
}

import org.ajoberstar.grgit.Grgit

repositories {
  jcenter()
}

task getCodeFormatScripts {
  description "Obtain the run-google-java-format scripts"
  doLast {
    def rgjfDir = "$projectDir/.run-google-java-format"
    if (! new File(rgjfDir).exists()) {
      def rgjfGit = Grgit.clone(dir: rgjfDir, uri: 'https://github.com/plume-lib/run-google-java-format.git')
    } else {
      def rgjfGit = Grgit.open(dir: rgjfDir)
      rgjfGit.pull()
    }
  }
}
-->


### Git pre-commit hook

Here is an example of what you might put in a Git pre-commit hook:
This only checks the files that are being comitted, which is much faster than checking all files.

```
CHANGED_JAVA_FILES=`git diff --staged --name-only --diff-filter=ACM | grep '\.java$' | grep -v '/ignored-directory/' ` || true
if [ ! -z "$CHANGED_JAVA_FILES" ]; then
    # Choose one of these lines, depending on your build system; adjust the final echo statement too:
    ant -silent update-run-google-java-format
    make --silent update-run-google-java-format
    ## For debugging:
    # echo "CHANGED_JAVA_FILES: ${CHANGED_JAVA_FILES}"
    ./.run-google-java-format/check-google-java-format.py ${CHANGED_JAVA_FILES} || (echo "Try running:  make reformat" && /bin/false)
fi
```

You will also want to add `.run-google-java-format` to your
`~/.gitignore-global` file or your project's `.gitignore` file.


#### Finding trailing spaces

google-java-format will complain about Java files with trailing spaces.
Here is code for your Git pre-commit hook that finds all files that have trailing spaces.

```
CHANGED_FILES=`git diff --staged --name-only --diff-filter=ACM | grep -v '.class$' | grep -v '.gz$'` | grep -v '.jar$'` | grep -v '.png$' | grep -v '.xcf$'` || true
if [ ! -z "$CHANGED_FILES" ]; then
    # echo "CHANGED_FILES: ${CHANGED_FILES}"
    FILES_WITH_TRAILING_SPACES=`grep -l -s '[[:blank:]]$' ${CHANGED_FILES} 2>&1` || true
    if [ ! -z "$FILES_WITH_TRAILING_SPACES" ]; then
        echo "Some files have trailing whitespace: ${FILES_WITH_TRAILING_SPACES}" && exit 1
    fi
fi
```


## Dealing with large changes when reformatting your codebase

When you first apply standard formatting, that may be disruptive to people
who have changes in their own branches/clones/forks.
(But, once you settle on consistent formatting, you will enjoy a number of
benefits.  Applying standard formatting to your codebase makes the code easier
to read.  It eases code review by eliminating comments about code style.
It also simplifies use of a version control system:  it reduces the
likelihood of merge conflicts due to formatting changes, and it ensures
that commits and pull requests don't intermingle substantive changes with
formatting changes.)

Here is a way to deal with upstream reformatting.

### For the person doing the reformatting

 1. Create a new branch and do your work there.

   ```git checkout -b reformat-gjf```

 2. Tag the commit before the whitespace change as "before reformatting".

   ```git tag -a before-reformatting -m "Code before running google-java-format"```

 3. Reformat by running a command such as
   `make reformat`,
   `ant reformat`, or
   `./gradlew reformat` (or whatever buildfile target you have set up).
 4. Examine the diffs to look for poor reformatting:

   ```git diff -w -b | grep -v '^[-+]import' | grep -v '^[-+]$'```

   (You may wish to use `grep -v` to exclude some additional lines,
   depending on your project.)

   Here are two examples of poor reformatting to look out for:

   * A single statement
     that is the body of an `if`/`for`/`while` statement.  google-java-format
     will move this onto the previous line with the boolean expression.  It's
     better to use curly braces `{}` on every `then` clause, `else` clause,
     and `for`/`while` body.  To find the poor reformatting (regexps in Emacs
     syntax):

       * Search for occurrences of `^\+.*\) return `.
       * Search for occurrences of `^\+.*\(if\|while\|for\) (.*) [^{]`.
       * Search for hunks that have fewer `+` than `-` lines.

     Add curly braces to get the body back on its own line.

   * Formatted Javadoc.  To preserve line breaks and horizontal formatting,
     you may wish to enclose parts of your Javadoc comments in `<pre>...</pre>`
     or use `<ul>` to format lists.

   (You can work in the branch where you are doing reformatting.
   Alternately, you might want to change your source code in the master
   branch, move the `before-reformatting` tag, and then start over with
   formatting.)

 5. Run tests
 6. Commit changes:

   ```git commit -m "Reformat code using google-java-format"```

 7. Tag the commit that does the whitespace change as "after reformatting".

   ```git tag -a after-reformatting -m "Code after running google-java-format"```

 8. Push both the commits and the tags:

   ```git push --tags```

### For a client to merge the massive upstream changes

Assuming before-reformatting is the last commit before reformatting
and after-reformatting is the reformatting commit:

 1. Merge in the commit before the reformatting into your branch.

     ```git merge before-reformatting```

   Or, if you have "myremote" configured as a remote, run these commands:

     ```
     git fetch myremote after-reformatting:after-reformatting
     git fetch myremote before-reformatting:before-reformatting
     ```

 2. Resolve any conflicts, run tests, and commit your changes.
 3. Merge in the reformatting commit, preferring all your own changes.

     ```git merge after-reformatting -s recursive -X ours```

 4. Reformat the code by running a command such as
   `make reformat`,
   `ant reformat`, or
   `./gradlew reformat` (or whatever buildfile target you have set up).
 5. Commit any formatting changes.
 6. Verify that this contains only changes you made (that is, the formatting
   changes were ignored):

     ```git diff after-reformatting...HEAD```

For a client of a client (such as a fork of a fork), the above instructions must be revised.


## Troubleshooting

If you get an error in
```urllib.urlretrieve(gjf_url, gjf_jar_path)```
then there is a problem with your installation of Python.

On MacOS Sierra, you can correct the problem by running these commands:

```
brew install openssl
brew install python@3 --with-brewed-openssl
brew link --overwrite python@3
```
