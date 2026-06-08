#!/usr/bin/env python3
"""Clean and validate YouTube IDs from standard input."""

import logging
import re
import sys

LOG_FILE = "pipeline_autid.log"

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

VALID_ID_PATTERN = re.compile(r"^[A-Za-z0-9_-]{11}$")


def is_valid_youtube_id(youtube_id):
    """Return True if the provided string is a valid YouTube ID."""
    return bool(VALID_ID_PATTERN.match(youtube_id))


def main():
    """Read YouTube IDs from stdin, print valid IDs, and log invalid IDs."""
    try:
        for line in sys.stdin:
            youtube_id = line.strip()

            if not youtube_id:
                continue

            if is_valid_youtube_id(youtube_id):
                print(youtube_id)
            else:
                logging.error("Invalid YouTube ID: %s", youtube_id)

    except KeyboardInterrupt:
        sys.exit(0)


if __name__ == "__main__":
    main()
