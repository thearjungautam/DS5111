"""Tests for transcript enrichment pipeline."""

import io
import json
import sys

from bin.enrich_transcripts import main


class MockGeminiResponse:
    """Mock Gemini response object."""

    def __init__(self, text_payload):
        """Store mock response text."""
        self.text = text_payload


def test_enrich_transcripts_streaming_pipeline(monkeypatch, capsys):
    """Verify enrichment pipeline without making live API calls."""

    def mock_generate_content(self, model, contents, config=None):
        """Return schema-compliant mock Gemini response."""
        mock_data = {
            "video_id": "ds5111_v001",
            "cleaned_text": "Welcome to class. Today we are testing mock frameworks.",
            "tech_terms": ["mock frameworks"],
            "book_names": [],
        }

        return MockGeminiResponse(json.dumps(mock_data))

    from google.genai.models import Models

    monkeypatch.setattr(Models, "generate_content", mock_generate_content)

    mock_input_row = {
        "video_id": "ds5111_v001",
        "raw_text": "00:01 Welcome to class. Today we are testing mock frameworks.",
    }

    mock_stdin = io.StringIO(json.dumps(mock_input_row) + "\n")
    monkeypatch.setattr(sys, "stdin", mock_stdin)
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    main(["--strategy", "gemini"])

    captured = capsys.readouterr()
    stdout_lines = captured.out.strip().split("\n")

    assert len(stdout_lines) == 1

    parsed_output = json.loads(stdout_lines[0])

    assert parsed_output["video_id"] == "ds5111_v001"
    assert "mock frameworks" in parsed_output["tech_terms"]


def test_enrich_transcripts_skips_bad_json(monkeypatch, capsys):
    """Verify malformed JSON input is skipped safely."""

    mock_stdin = io.StringIO("not valid json\n")
    monkeypatch.setattr(sys, "stdin", mock_stdin)
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    main(["--strategy", "gemini"])

    captured = capsys.readouterr()

    assert captured.out == ""


def test_mock_claude_strategy_pipeline(monkeypatch, capsys):
    """Verify the Claude mock strategy works without credentials or network calls."""
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)

    mock_input_row = {
        "video_id": "claude_test_001",
        "raw_text": "This row should pass through the mock Claude strategy.",
    }

    mock_stdin = io.StringIO(json.dumps(mock_input_row) + "\n")
    monkeypatch.setattr(sys, "stdin", mock_stdin)

    main(["--strategy", "claude"])

    captured = capsys.readouterr()
    stdout_lines = captured.out.strip().split("\n")

    assert len(stdout_lines) == 1

    parsed_output = json.loads(stdout_lines[0])

    assert parsed_output["video_id"] == "claude_test_001"
    assert "mock enrichment" in parsed_output["tech_terms"]
    assert parsed_output["cleaned_text"] == mock_input_row["raw_text"]
