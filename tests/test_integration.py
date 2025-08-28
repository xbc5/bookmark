"""Integration tests for the bookmark manager."""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock
import yaml

from bookmark.file_manager import ProjectTestFileManager
from bookmark.bookmark_creator import BookmarkCreator
from bookmark.bookmark_launcher import BookmarkLauncher
from bookmark.models import BookmarkManager


class TestBookmarkIntegration:
    """Integration tests for bookmark creation and launching workflows."""

    @pytest.fixture
    def temp_test_dir(self):
        """Create a temporary test directory within project bounds."""
        temp_dir = Path(tempfile.mkdtemp())
        yield temp_dir
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def file_manager(self, temp_test_dir):
        """Create a test file manager."""
        return ProjectTestFileManager(temp_test_dir)

    @pytest.fixture
    def bookmark_file(self, temp_test_dir):
        """Create a test bookmark file path."""
        return temp_test_dir / "test_bookmarks.txt"

    def test_complete_bookmark_lifecycle(self, file_manager, bookmark_file):
        """Test complete bookmark creation and retrieval lifecycle."""
        # Create a bookmark manager
        bookmark_manager = BookmarkManager(bookmark_file)

        # Ensure base directory exists
        file_manager.ensure_base_directory()
        bookmark_manager.ensure_file_exists()

        # Create test bookmarks
        from bookmark.models import Bookmark

        bookmark1 = Bookmark(
            name="test site one",
            url="https://test1.com",
            description="First test site",
            tags="testing,web",
        )

        bookmark2 = Bookmark(
            name="test site two",
            url="https://test2.com",
            description="Second test site",
            tags="demo,web",
        )

        # Add bookmarks
        bookmark_manager.add_bookmark(bookmark1)
        bookmark_manager.add_bookmark(bookmark2)

        # Read back bookmarks
        bookmarks = bookmark_manager.read_bookmarks()
        assert len(bookmarks) == 2

        # Verify first bookmark
        assert bookmarks[0].name == "Test Site One"
        assert bookmarks[0].url == "https://test1.com"
        assert bookmarks[0].description == "First test site"
        assert bookmarks[0].tags == "testing,web"

        # Verify second bookmark
        assert bookmarks[1].name == "Test Site Two"
        assert bookmarks[1].url == "https://test2.com"
        assert bookmarks[1].description == "Second test site"
        assert bookmarks[1].tags == "demo,web"

    def test_tags_management_workflow(self, file_manager):
        """Test tags are properly managed across bookmark operations."""
        # Initially no tags
        tags = file_manager.read_tags()
        assert tags == []

        # Add some tags
        file_manager.update_tags(["python", "web", "testing"])
        tags = file_manager.read_tags()
        assert tags == ["python", "testing", "web"]

        # Add more tags including duplicates
        file_manager.update_tags(["javascript", "web", "frontend"])
        tags = file_manager.read_tags()
        assert tags == ["frontend", "javascript", "python", "testing", "web"]

    def test_multiple_bookmark_files(self, file_manager, temp_test_dir):
        """Test managing bookmarks across multiple files."""
        work_file = temp_test_dir / "work_bookmarks.txt"
        personal_file = temp_test_dir / "personal_bookmarks.txt"

        work_manager = BookmarkManager(work_file)
        personal_manager = BookmarkManager(personal_file)

        # Create work bookmark
        from bookmark.models import Bookmark

        work_bookmark = Bookmark(
            "work site", "https://work.com", "Work stuff", "work,productivity"
        )
        work_manager.add_bookmark(work_bookmark)

        # Create personal bookmark
        personal_bookmark = Bookmark(
            "personal site", "https://personal.com", "Personal stuff", "personal,fun"
        )
        personal_manager.add_bookmark(personal_bookmark)

        # Verify separation
        work_bookmarks = work_manager.read_bookmarks()
        personal_bookmarks = personal_manager.read_bookmarks()

        assert len(work_bookmarks) == 1
        assert len(personal_bookmarks) == 1
        assert work_bookmarks[0].name == "Work Site"
        assert personal_bookmarks[0].name == "Personal Site"

    def test_config_file_integration(self, file_manager):
        """Test configuration file functionality."""
        # Default config
        config = file_manager.read_config()
        assert config["display_fields"] == ["name", "description", "url"]
        assert config["browser"] is None

        # Create custom config
        file_manager.ensure_base_directory()
        custom_config = {
            "display_fields": ["name", "url"],
            "browser": "firefox",
            "default_bookmark_file": "custom.txt",
        }

        with open(file_manager.config_file, "w") as f:
            yaml.dump(custom_config, f)

        # Verify custom config is loaded
        config = file_manager.read_config()
        assert config["display_fields"] == ["name", "url"]
        assert config["browser"] == "firefox"
        assert config["default_bookmark_file"] == "custom.txt"

    def test_bookmark_display_formatting(self, file_manager, bookmark_file):
        """Test bookmark display formatting with different field configurations."""
        # Create test bookmarks
        from bookmark.models import Bookmark

        bookmark = Bookmark(
            name="test site",
            url="https://test.com",
            description="A test site",
            tags="test,web",
        )

        # Test different display formats
        default_format = bookmark.matches_display_format(["name", "description", "url"])
        assert default_format == "Test Site|A test site|https://test.com"

        url_only_format = bookmark.matches_display_format(["name", "url"])
        assert url_only_format == "Test Site|https://test.com"

        with_tags_format = bookmark.matches_display_format(["name", "tags", "url"])
        assert with_tags_format == "Test Site|test,web|https://test.com"

    def test_empty_bookmark_file_handling(self, file_manager, bookmark_file):
        """Test handling of empty bookmark files."""
        # Create empty file
        bookmark_file.parent.mkdir(parents=True, exist_ok=True)
        bookmark_file.touch()

        bookmark_manager = BookmarkManager(bookmark_file)
        bookmarks = bookmark_manager.read_bookmarks()
        assert bookmarks == []

    def test_malformed_bookmark_recovery(self, file_manager, bookmark_file):
        """Test recovery from malformed bookmark entries."""
        # Create file with mixed valid and invalid entries
        bookmark_file.parent.mkdir(parents=True, exist_ok=True)
        with open(bookmark_file, "w") as f:
            f.write("Valid Site|https://valid.com|Good entry|web\n")
            f.write("Invalid Entry\n")  # Malformed
            f.write("\n")  # Blank line
            f.write("Another Valid|https://valid2.com||test\n")
            f.write("Too|Many|Fields|Here|Extra|Fields\n")  # Malformed

        bookmark_manager = BookmarkManager(bookmark_file)
        bookmarks = bookmark_manager.read_bookmarks()

        # Should only get valid bookmarks
        assert len(bookmarks) == 2
        assert bookmarks[0].name == "Valid Site"
        assert bookmarks[1].name == "Another Valid"

    def test_unicode_handling(self, file_manager, bookmark_file):
        """Test handling of unicode characters in bookmarks."""
        from bookmark.models import Bookmark

        # Create bookmark with unicode characters
        unicode_bookmark = Bookmark(
            name="测试网站",  # Chinese characters
            url="https://测试.com",
            description="Тест описание",  # Cyrillic characters
            tags="тест,网站",
        )

        bookmark_manager = BookmarkManager(bookmark_file)
        bookmark_manager.ensure_file_exists()
        bookmark_manager.add_bookmark(unicode_bookmark)

        # Read back and verify unicode preservation
        bookmarks = bookmark_manager.read_bookmarks()
        assert len(bookmarks) == 1

        saved_bookmark = bookmarks[0]
        assert saved_bookmark.name == "测试网站"
        assert saved_bookmark.url == "https://测试.com"
        assert saved_bookmark.description == "Тест описание"
        assert "тест" in saved_bookmark.tags
        assert "网站" in saved_bookmark.tags

    @patch("builtins.input")
    def test_bookmark_creator_workflow(self, mock_input, file_manager, bookmark_file):
        """Test the bookmark creation workflow."""
        # Mock user inputs
        mock_input.side_effect = [
            "My Test Site",  # name
            "https://example.com",  # url
            "A test site for integration testing",  # description
            "testing,integration,web",  # tags
        ]

        creator = BookmarkCreator(file_manager, bookmark_file)
        success = creator.create_bookmark()

        assert success is True

        # Verify bookmark was created
        bookmark_manager = BookmarkManager(bookmark_file)
        bookmarks = bookmark_manager.read_bookmarks()

        assert len(bookmarks) == 1
        bookmark = bookmarks[0]
        assert bookmark.name == "My Test Site"
        assert bookmark.url == "https://example.com"
        assert bookmark.description == "A test site for integration testing"
        assert bookmark.tags == "integration,testing,web"  # Should be sorted

    @patch("builtins.input")
    def test_bookmark_creator_name_validation(
        self, mock_input, file_manager, bookmark_file
    ):
        """Test bookmark creator handles invalid names."""
        # Mock user inputs - first input has pipe, second is valid
        mock_input.side_effect = [
            "My|Invalid|Name",  # invalid name with pipes
            "My Valid Name",  # valid name
            "https://example.com",  # url
            "",  # description (empty)
            "",  # tags (empty)
        ]

        creator = BookmarkCreator(file_manager, bookmark_file)

        # Mock print to capture validation message
        with patch("builtins.print") as mock_print:
            success = creator.create_bookmark()

        assert success is True

        # Verify validation message was shown
        mock_print.assert_any_call(
            "Name cannot contain pipe characters (|). Please try again."
        )

        # Verify bookmark was created with valid name
        bookmark_manager = BookmarkManager(bookmark_file)
        bookmarks = bookmark_manager.read_bookmarks()
        assert len(bookmarks) == 1
        assert bookmarks[0].name == "My Valid Name"
