#!/usr/bin/env python3
"""Validate enriched transcript JSONL records."""

import json
import sys


REQUIRED_FIELDS = {
    "video_id": str,
    "cleaned_text": str,
    "tech_terms": list,
    "book_names": list,
}


def validate_record(record):
    """Return True if record matches the expected schema."""
    for field_name, field_type in REQUIRED_FIELDS.items():
        if field_name not in record:
            return False

        if not isinstance(record[field_name], field_type):
            return False

    if not all(isinstance(item, str) for item in record["tech_terms"]):
        return False

    if not all(isinstance(item, str) for item in record["book_names"]):
        return False

    return True


def main():
    """Read JSONL records from stdin and validate each record."""
    valid_count = 0

    for line in sys.stdin:
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            sys.stderr.write("Invalid JSON line found.\n")
            sys.exit(1)

        if not validate_record(record):
            sys.stderr.write("Schema validation failed.\n")
            sys.exit(1)

        valid_count += 1

    sys.stdout.write(f"Validated {valid_count} records.\n")


if __name__ == "__main__":
    main()
