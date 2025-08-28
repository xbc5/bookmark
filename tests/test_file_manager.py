"""Tests for file management utilities."""

import pytest
import tempfile
import shutil
from pathlib import Path
import yaml

from bookmark.file_manager import BookmarkFileManager, ProjectTestFileManager


class TestBookmarkFileManager:
    """Test the BookmarkFileManager class."""

    @pytest.fixture
    def temp_base_dir(self):
        """Create a temporary base directory for testing."""
        temp_dir = Path(tempfile.mkdtemp())
        yield temp_dir
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def file_manager(self, temp_base_dir):
        """Create a file manager with temporary base directory."""
        return BookmarkFileManager(custom_base_dir=temp_base_dir)

    def test_initialization_default(self):
        """Test file manager initialization with default paths."""
        manager = BookmarkFileManager()

        # Should use ~/.bookmarks by default
        expected_base = Path.home() / ".bookmarks"
        assert manager.base_dir == expected_base
        assert manager.tags_file == expected_base / "tags.txt"
        assert manager.config_file == expected_base / "config.yaml"

    def test_initialization_custom_dir(self, temp_base_dir):
        """Test file manager initialization with custom directory."""
        manager = BookmarkFileManager(custom_base_dir=temp_base_dir)

        assert manager.base_dir == temp_base_dir
        assert manager.tags_file == temp_base_dir / "tags.txt"
        assert manager.config_file == temp_base_dir / "config.yaml"

    def test_ensure_base_directory_creates(self, file_manager):
        """Test that ensure_base_directory creates the directory."""
        # Remove the directory if it exists to test creation
        if file_manager.base_dir.exists():
            shutil.rmtree(file_manager.base_dir)

        assert not file_manager.base_dir.exists()
        file_manager.ensure_base_directory()
        assert file_manager.base_dir.exists()
        assert file_manager.base_dir.is_dir()

    def test_ensure_base_directory_exists(self, file_manager):
        """Test ensure_base_directory when directory already exists."""
        file_manager.base_dir.mkdir(parents=True, exist_ok=True)
        assert file_manager.base_dir.exists()

        # Should not raise error if already exists
        file_manager.ensure_base_directory()
        assert file_manager.base_dir.exists()

    def test_get_bookmark_file_path_default(self, file_manager):
        """Test getting bookmark file path with default name."""
        path = file_manager.get_bookmark_file_path()
        expected = file_manager.base_dir / "bookmarks.txt"
        assert path == expected

    def test_get_bookmark_file_path_custom_name(self, file_manager):
        """Test getting bookmark file path with custom name."""
        path = file_manager.get_bookmark_file_path("work.txt")
        expected = file_manager.base_dir / "work.txt"
        assert path == expected

    def test_get_bookmark_file_path_with_path(self, file_manager):
        """Test getting bookmark file path with path containing directories."""
        path = file_manager.get_bookmark_file_path("projects/work.txt")
        expected = file_manager.base_dir / "projects" / "work.txt"
        assert path == expected

    def test_read_tags_empty_file(self, file_manager):
        """Test reading tags from empty file."""
        file_manager.ensure_base_directory()
        file_manager.tags_file.touch()

        tags = file_manager.read_tags()
        assert tags == []

    def test_read_tags_nonexistent_file(self, file_manager):
        """Test reading tags when file doesn't exist."""
        tags = file_manager.read_tags()
        assert tags == []

    def test_read_tags_valid_file(self, file_manager):
        """Test reading tags from valid file."""
        file_manager.ensure_base_directory()

        with open(file_manager.tags_file, "w") as f:
            f.write("web\n")
            f.write("testing\n")
            f.write("code\n")
            f.write("python\n")

        tags = file_manager.read_tags()
        assert tags == ["code", "python", "testing", "web"]  # Should be sorted

    def test_read_tags_with_duplicates_and_case(self, file_manager):
        """Test reading tags handles duplicates and case normalization."""
        file_manager.ensure_base_directory()

        with open(file_manager.tags_file, "w") as f:
            f.write("WEB\n")
            f.write("testing\n")
            f.write("Web\n")  # Duplicate in different case
            f.write("TESTING\n")  # Duplicate in different case
            f.write("code\n")

        tags = file_manager.read_tags()
        assert tags == ["code", "testing", "web"]  # Deduplicated and sorted

    def test_read_tags_with_blank_lines(self, file_manager):
        """Test reading tags ignores blank lines."""
        file_manager.ensure_base_directory()

        with open(file_manager.tags_file, "w") as f:
            f.write("web\n")
            f.write("\n")  # Blank line
            f.write("testing\n")
            f.write("   \n")  # Line with spaces
            f.write("code\n")

        tags = file_manager.read_tags()
        assert tags == ["code", "testing", "web"]

    def test_update_tags_new_tags(self, file_manager):
        """Test updating tags with new tags."""
        new_tags = ["python", "web", "testing"]
        file_manager.update_tags(new_tags)

        # Verify tags file was created and contains tags
        assert file_manager.tags_file.exists()
        tags = file_manager.read_tags()
        assert tags == ["python", "testing", "web"]  # Should be sorted

    def test_update_tags_merge_existing(self, file_manager):
        """Test updating tags merges with existing tags."""
        # Create initial tags
        file_manager.ensure_base_directory()
        with open(file_manager.tags_file, "w") as f:
            f.write("existing\n")
            f.write("web\n")

        # Add new tags
        new_tags = ["python", "web", "testing"]  # "web" is duplicate
        file_manager.update_tags(new_tags)

        tags = file_manager.read_tags()
        assert tags == ["existing", "python", "testing", "web"]  # Merged and sorted

    def test_update_tags_empty_list(self, file_manager):
        """Test updating tags with empty list does nothing."""
        file_manager.update_tags([])

        # Should not create tags file
        assert not file_manager.tags_file.exists()

    def test_update_tags_normalizes_case(self, file_manager):
        """Test updating tags normalizes case."""
        new_tags = ["PYTHON", "Web", "TeStInG"]
        file_manager.update_tags(new_tags)

        tags = file_manager.read_tags()
        assert tags == ["python", "testing", "web"]

    def test_read_config_default(self, file_manager):
        """Test reading config returns defaults when file doesn't exist."""
        config = file_manager.read_config()

        expected = {
            "display_fields": ["name", "description", "url"],
            "browser": None,
            "default_bookmark_file": "bookmarks.txt",
        }
        assert config == expected

    def test_read_config_valid_file(self, file_manager):
        """Test reading valid config file."""
        file_manager.ensure_base_directory()

        config_data = {
            "display_fields": ["name", "url"],
            "browser": "firefox",
            "default_bookmark_file": "my_bookmarks.txt",
        }

        with open(file_manager.config_file, "w") as f:
            yaml.dump(config_data, f)

        config = file_manager.read_config()
        assert config["display_fields"] == ["name", "url"]
        assert config["browser"] == "firefox"
        assert config["default_bookmark_file"] == "my_bookmarks.txt"

    def test_read_config_partial_override(self, file_manager):
        """Test reading config file with partial overrides."""
        file_manager.ensure_base_directory()

        config_data = {
            "browser": "chrome"
            # Only override browser, keep other defaults
        }

        with open(file_manager.config_file, "w") as f:
            yaml.dump(config_data, f)

        config = file_manager.read_config()
        assert config["display_fields"] == ["name", "description", "url"]  # Default
        assert config["browser"] == "chrome"  # Overridden
        assert config["default_bookmark_file"] == "bookmarks.txt"  # Default

    def test_read_config_empty_file(self, file_manager):
        """Test reading empty config file returns defaults."""
        file_manager.ensure_base_directory()
        file_manager.config_file.touch()  # Create empty file

        config = file_manager.read_config()
        expected = {
            "display_fields": ["name", "description", "url"],
            "browser": None,
            "default_bookmark_file": "bookmarks.txt",
        }
        assert config == expected

    def test_read_config_invalid_yaml(self, file_manager):
        """Test reading config file with invalid YAML returns defaults."""
        file_manager.ensure_base_directory()

        with open(file_manager.config_file, "w") as f:
            f.write("invalid: yaml: content:\n  - malformed\n    - list")

        config = file_manager.read_config()
        expected = {
            "display_fields": ["name", "description", "url"],
            "browser": None,
            "default_bookmark_file": "bookmarks.txt",
        }
        assert config == expected


class TestProjectTestFileManager:
    """Test the ProjectTestFileManager class."""

    @pytest.fixture
    def temp_test_dir(self):
        """Create a temporary test directory."""
        temp_dir = Path(tempfile.mkdtemp())
        yield temp_dir
        shutil.rmtree(temp_dir)

    def test_project_test_file_manager_initialization(self, temp_test_dir):
        """Test that ProjectTestFileManager uses the provided test directory."""
        manager = ProjectTestFileManager(temp_test_dir)

        assert manager.base_dir == temp_test_dir
        assert manager.tags_file == temp_test_dir / "tags.txt"
        assert manager.config_file == temp_test_dir / "config.yaml"

    def test_project_test_file_manager_functionality(self, temp_test_dir):
        """Test that ProjectTestFileManager works like regular file manager."""
        manager = ProjectTestFileManager(temp_test_dir)

        # Test directory creation
        manager.ensure_base_directory()
        assert temp_test_dir.exists()

        # Test tags functionality
        manager.update_tags(["test", "project"])
        tags = manager.read_tags()
        assert tags == ["project", "test"]

        # Test config functionality
        config = manager.read_config()
        assert "display_fields" in config
