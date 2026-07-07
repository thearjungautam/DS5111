# pylint: disable=missing-module-docstring,missing-function-docstring,too-few-public-methods,unused-argument

import io
import json
import sys

from bin import enrich_transcripts


class MockGeminiResponse:
    """Mock Gemini response object."""

    def __init__(self, text_payload):
        self.text = text_payload


class MockModels:
    """Mock Gemini models service."""

    def generate_content(self, model, contents, config=None):
        mock_data = {
            "video_id": "ds5111_v001",
            "cleaned_text": "Welcome to class. Today we are testing mock frameworks.",
            "tech_terms": ["mock frameworks"],
            "book_names": [],
        }

        return MockGeminiResponse(json.dumps(mock_data))


class MockClient:
    """Mock Gemini client."""

    def __init__(self):
        self.models = MockModels()


def test_enrich_transcripts_streaming_pipeline(monkeypatch, capsys):
    """Verify enrichment pipeline without making live API calls."""
    monkeypatch.setattr(enrich_transcripts, "create_client", MockClient)

    mock_input_row = {
        "video_id": "ds5111_v001",
        "raw_text": "00:01 Welcome to class. Today we are testing mock frameworks.",
    }

    mock_stdin = io.StringIO(json.dumps(mock_input_row) + "\n")
    monkeypatch.setattr(sys, "stdin", mock_stdin)

    enrich_transcripts.main()

    captured = capsys.readouterr()
    stdout_lines = captured.out.strip().split("\n")

    assert len(stdout_lines) == 1

    parsed_output = json.loads(stdout_lines[0])

    assert parsed_output["video_id"] == "ds5111_v001"
    assert "mock frameworks" in parsed_output["tech_terms"]


def test_enrich_transcripts_skips_bad_json(monkeypatch, capsys):
    """Verify malformed JSON input is skipped safely."""
    monkeypatch.setattr(enrich_transcripts, "create_client", MockClient)

    mock_stdin = io.StringIO("not valid json\n")
    monkeypatch.setattr(sys, "stdin", mock_stdin)

    enrich_transcripts.main()

    captured = capsys.readouterr()

    assert captured.out == ""
