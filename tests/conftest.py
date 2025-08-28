"""Pytest configuration and fixtures for bookmark manager tests."""

import pytest
import tempfile
import shutil
from pathlib import Path


@pytest.fixture
def temp_project_dir():
    """Create a temporary directory within the project for testing.

    This fixture ensures all test operations stay within project boundaries
    as required by CLAUDE.md ABSOLUTE IMPERATIVES.
    """
    # Create temp directory within the project's test directory
    project_root = Path(__file__).parent.parent
    test_temp_dir = project_root / "tests" / "temp"
    test_temp_dir.mkdir(exist_ok=True)

    # Create unique temp directory for this test session
    temp_dir = Path(tempfile.mkdtemp(dir=test_temp_dir))

    yield temp_dir

    # Clean up after test
    if temp_dir.exists():
        shutil.rmtree(temp_dir)


@pytest.fixture
def mock_home_dir(temp_project_dir):
    """Create a mock home directory structure within project bounds."""
    mock_home = temp_project_dir / "mock_home"
    mock_home.mkdir()

    # Create .bookmarks directory
    bookmarks_dir = mock_home / ".bookmarks"
    bookmarks_dir.mkdir()

    return mock_home


@pytest.fixture(autouse=True)
def cleanup_test_artifacts():
    """Automatically clean up any test artifacts after each test."""
    yield

    # Clean up any temporary test directories in the tests folder
    project_root = Path(__file__).parent.parent
    test_temp_dir = project_root / "tests" / "temp"

    if test_temp_dir.exists():
        # Remove any leftover temporary directories
        for item in test_temp_dir.iterdir():
            if item.is_dir() and item.name.startswith("tmp"):
                try:
                    shutil.rmtree(item)
                except (PermissionError, OSError):
                    pass  # Best effort cleanup
