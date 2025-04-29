from pathlib import Path
from unittest.mock import mock_open, patch

import pytest

from ruff_report.save_report import (
    get_git_branchname,
    get_git_commithash,
    get_ruff_result_text,
    save,
)

# Mock data
MOCK_RUFF_OUTPUT = '{"mock": "data"}'
MOCK_BRANCH_NAME = "main"
MOCK_COMMIT_HASH = "abcdef1234567890"


@pytest.fixture
def mock_subprocess_run():
    with patch("subprocess.run") as mock_run:
        mock_run.return_value.stdout = MOCK_RUFF_OUTPUT
        mock_run.return_value.check_returncode = lambda: None
        yield mock_run


@pytest.fixture
def mock_subprocess_check_output():
    with patch("subprocess.check_output") as mock_check_output:

        def side_effect(*args, **kwargs):
            if "rev-parse" in args[0]:
                if "--abbrev-ref" in args[0]:
                    return MOCK_BRANCH_NAME
                return MOCK_COMMIT_HASH
            return ""

        mock_check_output.side_effect = side_effect
        yield mock_check_output


@pytest.fixture
def mock_open_file():
    with patch("builtins.open", mock_open()) as mock_file:
        yield mock_file


@pytest.fixture
def mock_mkdir():
    with patch.object(Path, "mkdir") as mock_mkdir:
        yield mock_mkdir


def test_save_report(
    mock_subprocess_run, mock_subprocess_check_output, mock_open_file, mock_mkdir
):
    # Call the save function
    result = save(
        target_root=Path("."),
        report_root=Path("test_reports"),
        report_name="test_report",
    )

    # Check if the subprocess.run was called with the expected command
    mock_subprocess_run.assert_called_once_with(
        ["ruff", "check", ".", "--output-format", "json"],
        cwd=Path("."),
        capture_output=True,
        text=True,
        check=False,
    )

    # Check if the directory was created
    mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)

    # Check if the file was opened and written to
    mock_open_file.assert_called_once()
    handle = mock_open_file()
    handle.write.assert_called_once_with(MOCK_RUFF_OUTPUT)

    # Check the result
    assert result == 0
