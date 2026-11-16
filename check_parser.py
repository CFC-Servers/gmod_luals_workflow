#!/usr/bin/env python3
import json
import os
import sys
import urllib.parse

ANNOTATION_TYPES = {1: "error", 2: "warning"}


def escape_data(s: str) -> str:
    return s.replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A")


def escape_property(s: str) -> str:
    return escape_data(s).replace(":", "%3A").replace(",", "%2C")


def relative_filename(file_uri: str) -> str:
    try:
        parsed_uri = urllib.parse.urlparse(file_uri)
        if parsed_uri.scheme != "file":
            return file_uri

        filename = urllib.parse.unquote(parsed_uri.path)

        return os.path.relpath(filename, os.getcwd())
    except Exception as e:
        print(f"::warning::Could not parse file URI '{file_uri}': {e}", file=sys.stderr)
        return file_uri


def read_source_lines(filename: str) -> list:
    try:
        with open(filename, encoding="utf-8", errors="replace") as source:
            return source.read().splitlines()
    except OSError:
        return []


# shortcut: the LuaLS formatter has no option for spaces inside grouping parentheses, remove when it gains one
def is_grouping_parenthesis_spacing(diagnostic: dict, source_lines: list) -> bool:
    if diagnostic.get("code") != "codestyle-check":
        return False
    if not diagnostic.get("message", "").startswith("unnecessary whitespace"):
        return False

    range_info = diagnostic.get("range") or {}
    start = range_info.get("start", {})
    end = range_info.get("end", {})

    try:
        character_before = source_lines[start["line"]][start["character"] - 1]
        character_after = source_lines[end["line"]][end["character"]]
    except (KeyError, IndexError):
        return False

    is_empty_parentheses = character_before == "(" and character_after == ")"

    return (character_before == "(" or character_after == ")") and not is_empty_parentheses


def one_based(position: dict, key: str):
    value = position.get(key)
    return None if value is None else value + 1


def main():
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(f"::error::Failed to parse JSON input: {e}", file=sys.stderr)
        sys.exit(1)

    if not data:
        sys.exit(0)

    found_error = False

    for file_uri, diagnostics in data.items():
        filename = relative_filename(file_uri)
        source_lines = read_source_lines(filename)

        for diagnostic in diagnostics:
            annotation_type = ANNOTATION_TYPES.get(diagnostic.get("severity"))
            if not annotation_type:
                continue
            if is_grouping_parenthesis_spacing(diagnostic, source_lines):
                continue

            message = diagnostic.get("message", "Unknown diagnostic")
            code = str(diagnostic.get("code", "Lua Diagnostic"))

            range_info = diagnostic.get("range") or {}
            start = range_info.get("start", {})
            end = range_info.get("end", {})

            location = {
                "line": one_based(start, "line"),
                "col": one_based(start, "character"),
                "endLine": one_based(end, "line"),
                "endColumn": one_based(end, "character"),
            }

            params = [f"file={escape_property(filename)}"]
            params += [f"{name}={value}" for name, value in location.items() if value is not None]
            params.append(f"title={escape_property(code)}")
            params_str = ",".join(params)

            plain_location_parts = [filename, location["line"], location["col"]]
            plain_location = ":".join(str(part) for part in plain_location_parts if part is not None)

            print(f"::{annotation_type} {params_str}::{escape_data(message)}")
            print(f"{plain_location}: {annotation_type} [{code}] {message}\n")

            if annotation_type == "error":
                found_error = True

    sys.exit(1 if found_error else 0)


if __name__ == "__main__":
    main()
