#!/usr/bin/env python3
import os
import json
import sys
import urllib.parse

def escape_data(s: str) -> str:
    return s.replace('%', '%25').replace('\r', '%0D').replace('\n', '%0A')

def main():
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(f"::error::Failed to parse JSON input: {e}", file=sys.stderr)
        sys.exit(1)

    # No errors!
    if not data:
        sys.exit(0)

    for file_uri, diagnostics in data.items():
        try:
            # Clean up the file path: remove file:// prefix and decode URL encoding
            parsed_uri = urllib.parse.urlparse(file_uri)
            if parsed_uri.scheme == 'file':
                filename = urllib.parse.unquote(parsed_uri.path)
                filename = os.path.relpath(filename, os.getcwd())
            else:
                filename = file_uri
        except Exception as e:
             print(f"::warning::Could not parse file URI '{file_uri}': {e}", file=sys.stderr)
             filename = file_uri

        for diagnostic in diagnostics:
            severity = diagnostic.get('severity')
            message = diagnostic.get('message', 'Unknown diagnostic')
            code = diagnostic.get('code', 'Lua Diagnostic')
            range_info = diagnostic.get('range')

            annotation_type = ""
            if severity == 1:
                annotation_type = "error"
            elif severity == 2:
                annotation_type = "warning"
            else:
                continue

            if not range_info:
                # Annotation without location info
                print(f"::{annotation_type} file={filename},title={code}::{escape_data(message)}")
                continue

            # Extract location details
            start_line = range_info.get('start', {}).get('line')
            start_col = range_info.get('start', {}).get('character')
            end_line = range_info.get('end', {}).get('line')
            end_col = range_info.get('end', {}).get('character')

            # Build params string, only including available location info
            params = [f"file={filename}"]
            if start_line is not None: params.append(f"line={start_line + 1}")
            if start_col is not None: params.append(f"col={start_col + 1}")
            if end_line is not None: params.append(f"endLine={end_line + 1}")
            if end_col is not None: params.append(f"endColumn={end_col + 1}")
            params.append(f"title={code}")

            params_str = ",".join(params)

            print(f"::{annotation_type} {params_str}::{escape_data(message)}")

    sys.exit(1)

if __name__ == "__main__":
    main()
