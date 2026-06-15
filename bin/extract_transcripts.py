#!/usr/bin/env python3
"""Extract YouTube transcripts from video IDs provided through stdin."""

import json
import logging
import os
import sys

from dotenv import load_dotenv
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.proxies import WebshareProxyConfig

load_dotenv()

logging.basicConfig(
    filename="pipeline/logs/pipeline_audit.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


def create_youtube_api():
    """Create a YouTubeTranscriptApi client with proxy support when credentials exist."""
    proxy_user = os.getenv("WEBSHARE_USER")
    proxy_pass = os.getenv("WEBSHARE_PASSWORD")

    if proxy_user and proxy_pass:
        logging.info(
            "Proxy credentials detected. Routing traffic via Webshare Residential network."
        )
        return YouTubeTranscriptApi(
            proxy_config=WebshareProxyConfig(
                proxy_username=proxy_user,
                proxy_password=proxy_pass,
            )
        )

    logging.warning("No proxy credentials found. Running with direct raw local IP routing.")
    return YouTubeTranscriptApi()


def main():
    """Read video IDs from stdin, fetch transcripts, and emit JSONL to stdout."""
    logging.info("Pipeline Step 2A (Raw Extraction) started.")

    ytt_api = create_youtube_api()

    for line in sys.stdin:
        video_id = line.strip()

        if not video_id:
            continue

        logging.info("Processing transcript extraction for video: %s", video_id)

        try:
            fetched_transcript = ytt_api.fetch(video_id)
            transcript_list = fetched_transcript.to_raw_data()

            raw_text = " ".join(
                f"[{item['start']}] {item['text']}" for item in transcript_list
            )

            payload = {
                "video_id": video_id,
                "raw_text": raw_text,
            }

            sys.stdout.write(json.dumps(payload) + "\n")
            sys.stdout.flush()

        except Exception as error:
            logging.error(
                "Failed to fetch YouTube transcript for %s: %s",
                video_id,
                str(error),
            )
            continue

    logging.info("Pipeline Step 2A finished.")


if __name__ == "__main__":
    main()
