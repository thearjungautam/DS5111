import io
import sys
import platform
import pytest

from clean_ids import main
from clean_ids import is_valid_youtube_id


def test_script_execution(monkeypatch, capsys):
    fake_input = io.StringIO("kcFsuxaJ1es\nasd123\n")

    monkeypatch.setattr(sys, "stdin", fake_input)

    main()

    captured = capsys.readouterr()

    assert captured.out == "kcFsuxaJ1es\n"


def test_os():
    assert platform.system() == "Linux"


def test_python_version():
    assert sys.version_info >= (3, 10)


@pytest.mark.xfail
def test_expected_failure():
    assert False


@pytest.mark.skip(reason="Feature not implemented")
def test_future_feature():
    pass


@pytest.mark.parametrize(
    "youtube_id,expected",
    [
        ("CctJNYYCPo0", True),
        ("kcFsuxaJ1es", True),
        ("abcd", False),
        ("1234", False),
        ("1234567890", False),
    ],
)
def test_validation(youtube_id, expected):
    assert is_valid_youtube_id(youtube_id) == expected
