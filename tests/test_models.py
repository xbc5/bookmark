"""Tests for bookmark models and validation."""

import pytest
from pathlib import Path
import tempfile
import shutil

from bookmark.models import Bookmark, BookmarkManager


class TestBookmark:
    """Test the Bookmark model."""

    def test_valid_bookmark_creation(self):
        """Test creating a valid bookmark with all fields."""
        bookmark = Bookmark(
            name="my test site",
            url="https://example.com",
            description="A test site",
            tags="web,testing",
        )

        assert bookmark.name == "My Test Site"  # Title case conversion
        assert bookmark.url == "https://example.com"
        assert bookmark.description == "A test site"
        assert bookmark.tags == "testing,web"  # Sorted and normalized

    def test_bookmark_with_empty_description(self):
        """Test creating bookmark without description."""
        bookmark = Bookmark(
            name="github", url="https://github.com", description="", tags="code,git"
        )

        assert bookmark.name == "Github"
        assert bookmark.url == "https://github.com"
        assert bookmark.description == ""
        assert bookmark.tags == "code,git"

    def test_bookmark_with_empty_tags(self):
        """Test creating bookmark without tags."""
        bookmark = Bookmark(
            name="news site", url="https://news.com", description="Daily news", tags=""
        )

        assert bookmark.name == "News Site"
        assert bookmark.url == "https://news.com"
        assert bookmark.description == "Daily news"
        assert bookmark.tags == ""

    def test_bookmark_minimal(self):
        """Test creating minimal bookmark with only name and URL."""
        bookmark = Bookmark(name="simple site", url="https://simple.com")

        assert bookmark.name == "Simple Site"
        assert bookmark.url == "https://simple.com"
        assert bookmark.description == ""
        assert bookmark.tags == ""

    def test_name_validation_pipe_character(self):
        """Test that pipe characters in names raise ValueError."""
        with pytest.raises(ValueError, match="Name cannot contain pipe characters"):
            Bookmark(name="My|Site", url="https://example.com")

    def test_name_title_case_normalization(self):
        """Test various name formats are converted to title case."""
        test_cases = [
            ("my test site", "My Test Site"),
            ("MY TEST SITE", "My Test Site"),
            ("mY tEsT sItE", "My Test Site"),
            ("test", "Test"),
            ("TEST", "Test"),
        ]

        for input_name, expected in test_cases:
            bookmark = Bookmark(name=input_name, url="https://example.com")
            assert bookmark.name == expected

    def test_tag_normalization(self):
        """Test tag normalization: lowercase, sorted, deduplicated."""
        test_cases = [
            (" Testing , WEB , Code ", "code,testing,web"),
            ("web,testing,web,code,testing", "code,testing,web"),
            ("WEB,TESTING", "testing,web"),
            ("", ""),
            ("  ", ""),
            ("single", "single"),
        ]

        for input_tags, expected in test_cases:
            bookmark = Bookmark(name="Test", url="https://example.com", tags=input_tags)
            assert bookmark.tags == expected

    def test_to_line_format(self):
        """Test conversion to pipe-delimited line format."""
        bookmark = Bookmark(
            name="My Test Site",
            url="https://example.com",
            description="A test site",
            tags="testing,web",
        )

        expected = "My Test Site|https://example.com|A test site|testing,web"
        assert bookmark.to_line() == expected

    def test_to_line_format_empty_fields(self):
        """Test line format with empty description and tags."""
        bookmark = Bookmark(
            name="Simple Site", url="https://simple.com", description="", tags=""
        )

        expected = "Simple Site|https://simple.com||"
        assert bookmark.to_line() == expected

    def test_from_line_valid(self):
        """Test creating bookmark from valid pipe-delimited line."""
        line = "My Example Bookmark|https://www.example.com|This is a test bookmark.|testing,example"
        bookmark = Bookmark.from_line(line)

        assert bookmark.name == "My Example Bookmark"
        assert bookmark.url == "https://www.example.com"
        assert bookmark.description == "This is a test bookmark."
        assert bookmark.tags == "example,testing"  # Should be sorted

    def test_from_line_empty_fields(self):
        """Test creating bookmark from line with empty fields."""
        line = "My Second Bookmark|https://another.com||"
        bookmark = Bookmark.from_line(line)

        assert bookmark.name == "My Second Bookmark"
        assert bookmark.url == "https://another.com"
        assert bookmark.description == ""
        assert bookmark.tags == ""

    def test_from_line_invalid_format(self):
        """Test that invalid line formats raise ValueError."""
        invalid_lines = [
            "name|url",  # Too few fields
            "name|url|desc|tags|extra",  # Too many fields
            "",  # Empty line
            "single_field",  # No pipes
        ]

        for line in invalid_lines:
            with pytest.raises(ValueError, match="Invalid bookmark format"):
                Bookmark.from_line(line)

    def test_matches_display_format(self):
        """Test formatting bookmark for display with specific fields."""
        bookmark = Bookmark(
            name="Test Site",
            url="https://test.com",
            description="A test site",
            tags="test,web",
        )

        # Default format
        result = bookmark.matches_display_format(["name", "description", "url"])
        assert result == "Test Site|A test site|https://test.com"

        # Custom format
        result = bookmark.matches_display_format(["name", "url"])
        assert result == "Test Site|https://test.com"

        # With tags
        result = bookmark.matches_display_format(["name", "tags"])
        assert result == "Test Site|test,web"

        # Invalid field
        result = bookmark.matches_display_format(["name", "invalid", "url"])
        assert result == "Test Site||https://test.com"


class TestBookmarkManager:
    """Test the BookmarkManager class."""

    @pytest.fixture
    def temp_bookmark_file(self):
        """Create a temporary bookmark file for testing."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
            temp_path = Path(f.name)
        yield temp_path
        if temp_path.exists():
            temp_path.unlink()

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        temp_dir = Path(tempfile.mkdtemp())
        yield temp_dir
        shutil.rmtree(temp_dir)

    def test_read_empty_file(self, temp_bookmark_file):
        """Test reading from an empty bookmark file."""
        manager = BookmarkManager(temp_bookmark_file)
        temp_bookmark_file.touch()  # Create empty file

        bookmarks = manager.read_bookmarks()
        assert bookmarks == []

    def test_read_nonexistent_file(self, temp_dir):
        """Test reading from a non-existent file."""
        nonexistent_file = temp_dir / "nonexistent.txt"
        manager = BookmarkManager(nonexistent_file)

        bookmarks = manager.read_bookmarks()
        assert bookmarks == []

    def test_read_bookmarks_with_blank_lines(self, temp_bookmark_file):
        """Test that blank lines are ignored when reading bookmarks."""
        with open(temp_bookmark_file, "w") as f:
            f.write("Test Site|https://test.com|Description|tag\n")
            f.write("\n")  # Blank line
            f.write("   \n")  # Line with only spaces
            f.write("Another Site|https://another.com||other\n")
            f.write("\n")  # Another blank line

        manager = BookmarkManager(temp_bookmark_file)
        bookmarks = manager.read_bookmarks()

        assert len(bookmarks) == 2
        assert bookmarks[0].name == "Test Site"
        assert bookmarks[1].name == "Another Site"

    def test_read_bookmarks_with_malformed_entries(self, temp_bookmark_file):
        """Test handling of malformed bookmark entries."""
        with open(temp_bookmark_file, "w") as f:
            f.write("Valid Site|https://valid.com|Description|tag\n")
            f.write("Invalid|Entry\n")  # Malformed - too few fields
            f.write("Another Valid|https://valid2.com||other\n")
            f.write("Too|Many|Fields|Here|Extra\n")  # Malformed - too many fields

        manager = BookmarkManager(temp_bookmark_file)
        bookmarks = manager.read_bookmarks()

        # Should only get the valid bookmarks
        assert len(bookmarks) == 2
        assert bookmarks[0].name == "Valid Site"
        assert bookmarks[1].name == "Another Valid"

    def test_add_bookmark(self, temp_bookmark_file):
        """Test adding a bookmark to a file."""
        manager = BookmarkManager(temp_bookmark_file)
        bookmark = Bookmark(
            name="test site",
            url="https://test.com",
            description="A test",
            tags="test,web",
        )

        manager.add_bookmark(bookmark)

        # Verify bookmark was added
        with open(temp_bookmark_file, "r") as f:
            content = f.read().strip()
            assert content == "Test Site|https://test.com|A test|test,web"

    def test_add_multiple_bookmarks(self, temp_bookmark_file):
        """Test adding multiple bookmarks."""
        manager = BookmarkManager(temp_bookmark_file)

        bookmark1 = Bookmark("first site", "https://first.com", "First", "test")
        bookmark2 = Bookmark("second site", "https://second.com", "Second", "demo")

        manager.add_bookmark(bookmark1)
        manager.add_bookmark(bookmark2)

        # Verify both bookmarks were added
        bookmarks = manager.read_bookmarks()
        assert len(bookmarks) == 2
        assert bookmarks[0].name == "First Site"
        assert bookmarks[1].name == "Second Site"

    def test_add_duplicate_bookmarks(self, temp_bookmark_file):
        """Test that duplicate bookmarks are allowed."""
        manager = BookmarkManager(temp_bookmark_file)
        bookmark = Bookmark("same site", "https://same.com", "Same", "duplicate")

        manager.add_bookmark(bookmark)
        manager.add_bookmark(bookmark)  # Add same bookmark again

        bookmarks = manager.read_bookmarks()
        assert len(bookmarks) == 2
        assert bookmarks[0].name == "Same Site"
        assert bookmarks[1].name == "Same Site"

    def test_ensure_file_exists_creates_file(self, temp_dir):
        """Test that ensure_file_exists creates the file if it doesn't exist."""
        bookmark_file = temp_dir / "new_bookmarks.txt"
        manager = BookmarkManager(bookmark_file)

        assert not bookmark_file.exists()
        manager.ensure_file_exists()
        assert bookmark_file.exists()

    def test_ensure_file_exists_creates_parent_directories(self, temp_dir):
        """Test that ensure_file_exists creates parent directories."""
        bookmark_file = temp_dir / "subdir" / "bookmarks.txt"
        manager = BookmarkManager(bookmark_file)

        assert not bookmark_file.parent.exists()
        manager.ensure_file_exists()
        assert bookmark_file.exists()
        assert bookmark_file.parent.exists()

    def test_add_bookmark_creates_parent_directories(self, temp_dir):
        """Test that adding a bookmark creates parent directories."""
        bookmark_file = temp_dir / "new_subdir" / "bookmarks.txt"
        manager = BookmarkManager(bookmark_file)

        bookmark = Bookmark("test", "https://test.com")
        manager.add_bookmark(bookmark)

        assert bookmark_file.exists()
        assert bookmark_file.parent.exists()
