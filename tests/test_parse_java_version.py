"""Tests for `parse_java_version` in run-google-java-format.py."""

import ast
import re
import unittest
from collections.abc import Callable
from typing import Any
from pathlib import Path

# Importing run-google-java-format.py would run it, so extract just the function.
script_path = Path(__file__).resolve().parent.parent / "run-google-java-format.py"
script_tree = ast.parse(script_path.read_text())
function_def = next(
    node
    for node in script_tree.body
    if isinstance(node, ast.FunctionDef) and node.name == "parse_java_version"
)
namespace: dict[str, Any] = {"re": re}
exec(compile(ast.Module([function_def], []), str(script_path), "exec"), namespace)  # noqa: S102
parse_java_version: Callable[[str], int] = namespace["parse_java_version"]


class TestParseJavaVersion(unittest.TestCase):
    """Tests for `parse_java_version`."""

    def test_versions(self) -> None:
        """Test the output of various JDKs."""
        cases = {
            'java version "1.7.0_80"\n': 7,
            'openjdk version "1.8.0_292"\n': 8,
            'openjdk version "10.0.2" 2018-07-17\n': 10,
            'openjdk version "11.0.11" 2021-04-20\n': 11,
            'openjdk version "16.0.2" 2021-07-20\n': 16,
            'java version "17" 2021-09-14 LTS\n': 17,
            'openjdk version "21.0.5" 2024-10-15 LTS\n': 21,
            'openjdk version "26-ea" 2026-03-17\n': 26,
        }
        for java_version_string, expected in cases.items():
            with self.subTest(java_version_string=java_version_string):
                self.assertEqual(parse_java_version(java_version_string), expected)

    def test_preceding_line(self) -> None:
        """Test output that has a line before the version line."""
        java_version_string = (
            'Picked up JAVA_TOOL_OPTIONS: -Dhttp.proxyPort="8080"\n'
            'openjdk version "17.0.1" 2021-10-19\n'
            "OpenJDK Runtime Environment (build 17.0.1+12-39)\n"
        )
        self.assertEqual(parse_java_version(java_version_string), 17)

    def test_no_version(self) -> None:
        """Test output that contains no version line."""
        with self.assertRaises(Exception):  # noqa: B017, PT027
            parse_java_version("Error: could not find java.dll\n")


if __name__ == "__main__":
    unittest.main()
