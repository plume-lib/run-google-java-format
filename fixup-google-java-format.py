#!/usr/bin/env python3
"""The google-java-format program (https://github.com/google/google-java-format)
reformats Java source code, but it creates poor formatting for annotations
in comments.
Run this script on files after running google-java-format, and it will perform
small changes in place to improve formatting of annotations in comments.
If called with no arguments, it reads from and writes to standard output.

You typically will not run this program directly; it is run by
run-google-java-format.py.
"""

from __future__ import print_function

import os
import os.path
import re
import sys


def eprint(*args, **kwargs):
    "Print to standard error"
    print(*args, file=sys.stderr, **kwargs)


# pylint: disable=line-too-long, multiple-statements

# These are type annotations, which should NOT go on their own line.
# A type annotation's @Target annotation contains "TYPE_USE".
# This includes private type annotations used in Checker Framework tests.
# To generate this list:
#   grep --recursive --files-with-matches -e '^@Target\b.*TYPE_USE' $CHECKERFRAMEWORK/checker/src/test $CHECKERFRAMEWORK/checker-qual/src/main/java $CHECKERFRAMEWORK/framework/src/main/java $CHECKERFRAMEWORK/docs/examples/units-extension $CHECKERFRAMEWORK/framework/src/test/java $t/checker-framework-fork-t-rasmud-branch-nondet-checker/checker-qual/src/main/java/org/checkerframework/checker/determinism | grep -v '~' | sed 's/.*\///' | awk '{print $1} END {print "NotNull.java"; print "UbTop.java"; print "LbTop.java"; print "UB_TOP.java"; print "LB_TOP.java";}' | sed 's/\(.*\)\.java/        "\1",/' | sort | uniq > type-qualifiers.txt
typeAnnotations = set(
    [
        "A",
        "ACCBottom",
        "Acceleration",
        "ACCTop",
        "AinferBottom",
        "AlwaysSafe",
        "Angle",
        "AnnoWithStringArg",
        "Area",
        "ArrayLen",
        "ArrayLenRange",
        "ArrayWithoutPackage",
        "AwtAlphaCompositingRule",
        "AwtColorSpace",
        "AwtCursorType",
        "AwtFlowLayout",
        "B",
        "BinaryName",
        "BinaryNameInUnnamedPackage",
        "BinaryNameOrPrimitiveType",
        "BinaryNameWithoutPackage",
        "BoolVal",
        "Bottom",
        "BottomQualifier",
        "BottomThis",
        "BottomVal",
        "C",
        "CalledMethods",
        "CalledMethodsBottom",
        "CalledMethodsPredicate",
        "CalledMethodsTop",
        "CanonicalName",
        "CanonicalNameAndBinaryName",
        "CanonicalNameOrEmpty",
        "CanonicalNameOrPrimitiveType",
        "CCBottom",
        "CCTop",
        "cd",
        "ClassBound",
        "ClassGetName",
        "ClassGetSimpleName",
        "ClassVal",
        "ClassValBottom",
        "CompilerMessageKey",
        "CompilerMessageKeyBottom",
        "Constant",
        "Critical",
        "Current",
        "D",
        "DefaultType",
        "degrees",
        "Det",
        "DisbarUseBottom",
        "DisbarUseTop",
        "DotSeparatedIdentifiers",
        "DotSeparatedIdentifiersOrPrimitiveType",
        "DoubleVal",
        "E",
        "Encrypted",
        "EnhancedRegex",  # temporary?
        "EnumVal",
        "Even",
        "F",
        "FBCBottom",
        "FEBottom",
        "FEBot",
        "Fenum",
        "FenumBottom",
        "FenumTop",
        "FETop",
        "FieldDescriptor",
        "FieldDescriptorForPrimitive",
        "FieldDescriptorForPrimitiveOrArrayInUnnamedPackage",
        "FieldDescriptorWithoutPackage",
        "FlowExp",
        "Force",
        "Format",
        "FormatBottom",
        "FqBinaryName",
        "Frequency",
        "FullyQualifiedName",
        "g",
        "GTENegativeOne",
        "GuardedBy",
        "GuardedByBottom",
        "GuardedByUnknown",
        "GuardSatisfied",
        "h",
        "H1Bot",
        "H1Invalid",
        "H1Poly",
        "H1S1",
        "H1S2",
        "H1Top",
        "H2Bot",
        "H2Poly",
        "H2S1",
        "H2S2",
        "H2Top",
        "Hz",
        "I18nFormat",
        "I18nFormatBottom",
        "I18nFormatFor",
        "I18nInvalidFormat",
        "I18nUnknownFormat",
        "Identifier",
        "IdentifierOrArray",
        "IdentifierOrPrimitiveType",
        "ImplicitAnno",
        "IndexFor",
        "IndexOrHigh",
        "IndexOrLow",
        "Initialized",
        "InitializedFields",
        "InitializedFieldsBottom",
        "InitializedFieldsPredicate",
        "InternalForm",
        "Interned",
        "InternedDistinct",
        "IntRange",
        "IntVal",
        "InvalidFormat",
        "K",
        "KeyFor",
        "KeyForBottom",
        "KeyForType",
        "kg",
        "kHz",
        "km",
        "km2",
        "km3",
        "kmPERh",
        "kN",
        "LbTop",
        "LB_TOP",
        "LeakedToResult",
        "Length",
        "LengthOf",
        "LessThan",
        "LessThanBottom",
        "LessThanUnknown",
        "LocalizableKey",
        "LocalizableKeyBottom",
        "Localized",
        "LowerBoundBottom",
        "LowerBoundUnknown",
        "LTEqLengthOf",
        "LTLengthOf",
        "LTOMLengthOf",
        "Luminance",
        "m",
        "m2",
        "m3",
        "Mass",
        "MatchesRegex",
        "MaybeAliased",
        "MaybeDerivedFromConstant",
        "MaybePresent",
        "MaybeThis",
        "MethodDescriptor",
        "MethodVal",
        "MethodValBottom",
        "min",
        "MinLen",
        "mm",
        "mm2",
        "mm3",
        "mol",
        "MonotonicNonNull",
        "MonotonicNonNullType",
        "MonotonicOdd",
        "mPERs",
        "mPERs2",
        "MustCall",
        "MustCallAlias",
        "MustCallUnknown",
        "N",
        "NegativeIndexFor",
        "NewObject",
        "NonConstant",
        "NonDet",
        "NonLeaked",
        "NonNegative",
        "NonNull",
        "NonNullType",
        "NonRaw",
        "NotCalledMethods",
        "NotNull",
        "NotQualifier",
        "NTDBottom",
        "NTDMiddle",
        "NTDSide",
        "NTDTop",
        "Nullable",
        "NullableType",
        "Odd",
        "OptionalBottom",
        "OrderNonDet",
        "Parent",
        "PatternA",
        "PatternAB",
        "PatternAC",
        "PatternB",
        "PatternBC",
        "PatternBottomFull",
        "PatternBottomPartial",
        "PatternC",
        "PatternUnknown",
        "Poly",
        "PolyAll",
        "PolyConstant",
        "PolyDet",
        "PolyEncrypted",
        "PolyFenum",
        "PolyIndex",
        "PolyInitializedFields",
        "PolyInterned",
        "PolyKeyFor",
        "PolyLength",
        "PolyLowerBound",
        "PolyMustCall",
        "PolyNull",
        "PolyNullType",
        "PolyPresent",
        "PolyRaw",
        "PolyReflection",
        "PolyRegex",
        "PolySameLen",
        "PolySignature",
        "PolySigned",
        "PolyTainted",
        "PolyTestAccumulation",
        "PolyTypeDeclDefault",
        "PolyUI",
        "PolyUnit",
        "PolyUpperBound",
        "PolyValue",
        "PolyVariableNameDefault",
        "Positive",
        "Present",
        "PrimitiveType",
        "PropertyKey",
        "PropertyKeyBottom",
        "PurityUnqualified",
        "Qualifier",
        "radians",
        "Raw",
        "ReflectBottom",
        "Regex",
        "RegexBottom",
        "RegexNNGroups",  # temporary?
        "ReportUnqualified",
        "s",
        "SameLen",
        "SameLenBottom",
        "SameLenUnknown",
        "SearchIndexBottom",
        "SearchIndexFor",
        "SearchIndexUnknown",
        "Sibling1",
        "Sibling2",
        "SiblingWithFields",
        "SignatureBottom",
        "Signed",
        "SignednessBottom",
        "SignednessGlb",
        "SignedPositive",
        "SignedPositiveFromUnsigned",
        "Speed",
        "StringVal",
        "SubQual",
        "Substance",
        "SubstringIndexBottom",
        "SubstringIndexFor",
        "SubstringIndexUnknown",
        "SuperQual",
        "SwingBoxOrientation",
        "SwingCompassDirection",
        "SwingElementOrientation",
        "SwingHorizontalOrientation",
        "SwingSplitPaneOrientation",
        "SwingTextOrientation",
        "SwingTitleJustification",
        "SwingTitlePosition",
        "SwingVerticalOrientation",
        "t",
        "Tainted",
        "Temperature",
        "TestAccumulation",
        "TestAccumulationBottom",
        "TestAccumulationPredicate",
        "This",
        "Time",
        "Top",
        "TypeDeclDefaultBottom",
        "TypeDeclDefaultMiddle",
        "TypeDeclDefaultTop",
        "UbTop",
        "UB_TOP",
        "UI",
        "UnderInitialization",
        "Unique",
        "UnitsBottom",
        "UnknownClass",
        "UnknownCompilerMessageKey",
        "UnknownFormat",
        "UnknownInitialization",
        "UnknownInterned",
        "UnknownKeyFor",
        "UnknownLocalizableKey",
        "UnknownLocalized",
        "UnknownMethod",
        "UnknownPropertyKey",
        "UnknownRegex",
        "UnknownSignedness",
        "UnknownThis",
        "UnknownUnits",
        "UnknownVal",
        "Unsigned",
        "Untainted",
        "UpperBoundBottom",
        "UpperBoundLiteral",
        "UpperBoundUnknown",
        "Value",
        "VariableNameDefaultBottom",
        "VariableNameDefaultMiddle",
        "VariableNameDefaultTop",
        "Volume",
        "WholeProgramInferenceBottom",
    ]
)

# File .type-annotations can add to the typeAnnotations variable.
if os.path.isfile(".type-annotations"):
    with open(".type-annotations") as ta:
        exec(ta.read())

debug = False
# debug = True


def debug_print(*args, **kwargs):
    """Print, only if the debug variable is set."""
    if debug:
        print(*args, **kwargs)


# Two annotations in a row, or an annotation abutting array brackets "[]".
# Space is inserted between.
abuttingannoRegex = re.compile(r"(/\*@[A-Za-z0-9_]+\*/)(\[\]|/\*@[A-Za-z0-9_]+\*/)")
# Voodoo annotation with extra space after
voodootrailingspaceRegex = re.compile(r"(/\*>>> ?@.*\bthis\*/) (\))")

# Matches the argument to an annotation.
# 3 cases:
#   ()
#   (".*")
#   (.*)
# The regex tries to safely permit "()" within a string in an annotation, such as
#   @GuardedBy("c1.getFieldPure2()")
annoargRegex = r'(?: *(?:\( *\)|\( *"[^"]*" *\)|\([^")][^)]*\)))?'
# Matches an annotation
annoRegex = r"@[A-Za-z0-9_.]+" + annoargRegex

# Matches, at the end of its line (in capturing group 2):
#  * An annotation
#    This is a bit dangerous!  It might be within a comment.
#    The script tries to heuristically detect this.
#  * An annotation in comments
#  * a comment like /*offset = */ that should appear right
#    before the argument it documents.
#    (Supported in main google-java-format as of April 26, 2017, but not yet in a release:
#    https://github.com/google/google-java-format/commit/ca0c4d90cdbb46b3a2bf9c2b83d0bd558cccc41e )
# The annotation will be moved to the beginning of the following line,
# if it appears in typeAnnotations.
trailingannoRegex = re.compile(
    r"^(.*?)[ \t]*("
    + annoRegex
    + r"|/\*"
    + annoRegex
    + r"\*/|/\* *[A-Za-z0-9_]+ *= *\*/)$"
)

whitespaceRegex = re.compile(r"^([ \t]*).*$")

emptylineRegex = re.compile(r"^[ \t]*$")

# Heuristic: matches if the line might be within a //, /*, or Javadoc comment.
withinCommentRegex = re.compile(r"//|/\*(?!.*\/*/)|^[ \t]*\*[ \t]")

startsWithCommentRegex = re.compile(r"^[ \t]*(//|/\*$|/\*[^@]|\*|void\b)")


def insert_after_whitespace(insertion, s):
    """Return s, with insertion inserted after its leading whitespace."""
    m = re.match(whitespaceRegex, s)
    return s[0 : m.end(1)] + insertion + s[m.end(1) :]


def fixup_loop(infile, outfile):
    """Fix up formatting while reading from infile and writing to outfile."""
    prev = ""  # previous line, which might end with a type annotation.
    for line in infile:
        # Handle trailing space after a voodoo comment
        line = voodootrailingspaceRegex.sub(r"\1\2", line)
        # Handle abutting annotations in comments
        m = re.search(abuttingannoRegex, line)
        while m:
            debug_print("found abutting", line)
            line = line[0 : m.end(1)] + " " + line[m.start(2) :]
            m = re.search(abuttingannoRegex, line)
        # Don't move an annotation to the start of a comment line
        if re.search(startsWithCommentRegex, line):
            m = None
            debug_print("Don't prepend to comment", prev, line)
        else:
            # Handle annotations at end of line that should be at beginning of
            # next line.
            m = re.search(trailingannoRegex, prev)
            debug_print("trailing? (pre-loop)", m, prev, line)
        while m:
            debug_print("found trailing", prev, line)
            anno = m.group(2)
            if not base_annotation(anno) in typeAnnotations:
                break
            debug_print("prev was:", prev)
            candidate_prev = prev[0 : m.end(1)] + prev[m.end(2) :]
            debug_print("candidate_prev is :", candidate_prev)
            if re.search(withinCommentRegex, candidate_prev):
                debug_print("withinCommentRegex prohibits action")
                break
            prev = candidate_prev
            debug_print("prev is:", prev)
            if re.search(emptylineRegex, prev):
                prev = ""
                debug_print("prev is empty")
            debug_print("line was:", line)
            line = insert_after_whitespace(anno + " ", line)
            debug_print("line is :", line)
            m = re.search(trailingannoRegex, prev)
            debug_print("trailing? (post-loop-body)", m, prev, line)
            if re.search(" try \($", prev):
                candidate_line = prev.rstrip() + line.lstrip()
                if len(candidate_line) < 100:
                    line = candidate_line
                    prev = ""
                debug_print("joined, now line is:", line)
            else:
                debug_print("no try match for", prev, line)
        outfile.write(prev)
        prev = line
    outfile.write(prev)


def base_annotation(annotation):
    """Remove leading and trailing comment characters, spaces, arguments, and at sign.
    Example: base_annotation('/*@RequiresNonNull("FileIO.data_trace_state")*/' => 'RequiresNonNull'"""
    debug_print("base_annotation <=", annotation)

    # Remove comments
    if annotation.startswith("/*"):
        annotation = annotation[2:]
    if annotation.endswith("*/"):
        annotation = annotation[:-2]

    # Remove arguments
    idx = annotation.find("(")
    if idx != -1:
        annotation = annotation[0:idx]

    # Remove package names
    idx = annotation.rfind(".")
    if idx != -1:
        annotation = annotation[idx + 1 :]

    annotation = annotation.strip()
    if annotation.startswith("@"):
        annotation = annotation[1:]
    debug_print("base_annotation =>", annotation)
    return annotation


if len(sys.argv) == 1:
    fixup_loop(sys.stdin, sys.stdout)
else:
    for fname in sys.argv[1:]:
        outfname = fname + ".out"
        with open(fname, "r") as infile:
            with open(outfname, "w") as outfile:
                fixup_loop(infile, outfile)
        os.rename(outfname, fname)
