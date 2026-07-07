# pylint: disable=missing-module-docstring,missing-function-docstring,too-few-public-methods,unused-argument,import-outside-toplevel,unused-import
import io
import json
import sys

import pytest
from youtube_transcript_api import YouTubeTranscriptApi

from bin.extract_transcripts import main


class MockTranscriptContainer:
    """Mimics the transcript API response."""

    def to_raw_data(self):
        return [
            {"start": 10.5, "text": "Automated container tracking loop text entry."}
        ]


def test_extract_transcripts_main_pipeline_stream(monkeypatch, capsys):
    """Test successful transcript extraction without calling the internet."""

    def stubbed_fetch_route(self, video_id):
        assert video_id == "fake_video_999"
        return MockTranscriptContainer()

    monkeypatch.setattr(YouTubeTranscriptApi, "fetch", stubbed_fetch_route)

    mock_input_stream = io.StringIO("fake_video_999\n")
    monkeypatch.setattr(sys, "stdin", mock_input_stream)

    main()

    captured_output = capsys.readouterr()
    stdout_lines = captured_output.out.strip().split("\n")

    assert len(stdout_lines) == 1

    parsed_json_line = json.loads(stdout_lines[0])

    assert parsed_json_line["video_id"] == "fake_video_999"
    assert "Automated container tracking" in parsed_json_line["raw_text"]


def test_extract_transcripts_handles_fetch_error(monkeypatch, capsys):
    """Test that fetch errors are handled without crashing."""

    def stubbed_fetch_error(self, video_id):
        raise RuntimeError("Transcript unavailable")

    monkeypatch.setattr(YouTubeTranscriptApi, "fetch", stubbed_fetch_error)

    mock_input_stream = io.StringIO("bad_video_id\n")
    monkeypatch.setattr(sys, "stdin", mock_input_stream)

    main()

    captured_output = capsys.readouterr()

    assert captured_output.out == ""
