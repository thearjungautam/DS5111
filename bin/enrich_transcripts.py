#!/usr/bin/env python3
"""Enrich transcript records using Gemini."""

import json
import logging
import os
import sys
from abc import ABC, abstractmethod
import argparse

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

class TranscriptEnricher(ABC):
    """Abstract contract for transcript enrichment strategies."""

    @abstractmethod
    def enrich(self, video_id: str, raw_text: str) -> dict:
        """Return structured enrichment data for a transcript."""
        raise NotImplementedError


class GeminiEnricher(TranscriptEnricher):
    """Gemini implementation of the transcript enrichment strategy."""

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





    def __init__(self, api_key: str, model: str = "gemini-2.5-flash"):
        self.api_key = api_key
        self.model = model

    def enrich(self, video_id: str, raw_text: str) -> dict:
        """Enrich a transcript using Gemini and return structured data."""
        try:
            client = genai.Client(api_key=self.api_key)

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
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=self.response_schema,
                ),
            )

            return json.loads(response.text)

        except Exception as error:
            raise RuntimeError(
                f"Gemini enrichment failed for {video_id}: {error}"
            ) from error


class MockClaudeEnricher(TranscriptEnricher):
    """Deterministic stand-in for a Claude-based enrichment strategy."""

    def enrich(self, video_id: str, raw_text: str) -> dict:
        """Return deterministic mock enrichment output."""
        return {
            "video_id": video_id,
            "cleaned_text": raw_text,
            "tech_terms": ["mock enrichment"],
            "book_names": [],
        }


class EnrichmentEngine:
    """Pipeline engine that delegates transcript enrichment to a strategy."""

    def __init__(self, strategy: TranscriptEnricher):
        self.strategy = strategy

    def run_stream(self):
        """Process transcript JSONL records from stdin and emit enriched JSONL."""
        for line in sys.stdin:
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                logging.error("Malformed JSON input row.")
                continue

            video_id = row.get("video_id")
            raw_text = row.get("raw_text")

            try:
                enriched = self.strategy.enrich(video_id, raw_text)
            except RuntimeError as error:
                logging.error(
                    "Failed to enrich transcript for %s: %s",
                    video_id,
                    error,
                )
                continue

            enriched["video_id"] = video_id

            sys.stdout.write(json.dumps(enriched) + "\n")
            sys.stdout.flush()





def main(argv=None):
    """Select an enrichment strategy and run the pipeline."""
    parser = argparse.ArgumentParser(
        description="Transcript enrichment pipeline."
    )
    parser.add_argument(
        "--strategy",
        choices=["gemini", "claude"],
        default="gemini",
        help="Enrichment strategy to use.",
    )
    args = parser.parse_args(argv)
    selected_strategy = None
    if args.strategy == "gemini":
        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            logging.critical("GEMINI_API_KEY not found in environment.")
            sys.exit(1)

        selected_strategy = GeminiEnricher(api_key=api_key)

    elif args.strategy == "claude":
        selected_strategy = MockClaudeEnricher()

    engine = EnrichmentEngine(selected_strategy)
    engine.run_stream()

if __name__ == "__main__":
    main()
