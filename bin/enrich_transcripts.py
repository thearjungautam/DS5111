#!/usr/bin/env python3
"""Enrich transcript records using Gemini."""

import json
import logging
import os
import sys

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

response_schema = {
    "type": "object",
    "properties": {
        "video_id": {"type": "string"},
        "cleaned_text": {"type": "string"},
        "tech_terms": {
            "type": "array",
            "items": {"type": "string"},
        },
        "book_names": {
            "type": "array",
            "items": {"type": "string"},
        },
    },
    "required": [
        "video_id",
        "cleaned_text",
        "tech_terms",
        "book_names",
    ],
}


def create_client():
    """Create Gemini client after checking API key."""
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        logging.critical("GEMINI_API_KEY not found in environment.")
        sys.exit(1)

    return genai.Client(api_key=api_key)


def main():
    """Read transcript rows from stdin and enrich them."""
    client = create_client()

    for line in sys.stdin:
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            logging.error("Malformed JSON input row.")
            continue

        video_id = row.get("video_id")
        raw_text = row.get("raw_text")

        prompt = f"""
Clean the transcript text.

Return:
- cleaned_text
- tech_terms
- book_names

video_id: {video_id}

Transcript:
{raw_text}
"""

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=response_schema,
            ),
        )

        try:
            enriched = json.loads(response.text)
        except json.JSONDecodeError:
            logging.error("Model returned invalid JSON.")
            continue

        enriched["video_id"] = video_id

        sys.stdout.write(json.dumps(enriched) + "\n")
        sys.stdout.flush()


if __name__ == "__main__":
    main()
