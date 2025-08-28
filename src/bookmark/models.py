"""Data models for the bookmark manager."""

from dataclasses import dataclass
from pathlib import Path


@dataclass
class Bookmark:
    """A single bookmark entry.

    Represents a bookmark with name, URL, description, and tags following
    the pipe-delimited format: name|url|description|tags
    """

    name: str
    url: str
    description: str = ""
    tags: str = ""

    def __post_init__(self) -> None:
        """Validate and normalize bookmark fields after initialization."""
        self.name = self._normalize_name(self.name)
        self.tags = self._normalize_tags(self.tags)

    def _normalize_name(self, name: str) -> str:
        """Normalize the bookmark name to title case and validate format.

        Args:
            name: The raw name input

        Returns:
            The normalized name in title case

        Raises:
            ValueError: If name contains pipe characters
        """
        if "|" in name:
            raise ValueError("Name cannot contain pipe characters")
        return name.title()

    def _normalize_tags(self, tags: str) -> str:
        """Normalize tags to lowercase, sorted, comma-separated format.

        Args:
            tags: The raw tags input (comma-separated)

        Returns:
            Normalized tags string (lowercase, sorted, deduplicated)
        """
        if not tags.strip():
            return ""

        # Split, strip whitespace, convert to lowercase, remove duplicates
        tag_list = [tag.strip().lower() for tag in tags.split(",")]
        tag_list = [tag for tag in tag_list if tag]  # Remove empty strings
        unique_tags = list(
            dict.fromkeys(tag_list),
        )  # Preserve order while removing duplicates
        unique_tags.sort()  # Sort alphabetically

        return ",".join(unique_tags)

    def to_line(self) -> str:
        """Convert bookmark to pipe-delimited line format.

        Returns:
            Bookmark as a pipe-delimited string
        """
        return f"{self.name}|{self.url}|{self.description}|{self.tags}"

    @classmethod
    def from_line(cls, line: str) -> "Bookmark":
        """Create a Bookmark from a pipe-delimited line.

        Args:
            line: A pipe-delimited bookmark line

        Returns:
            A Bookmark instance

        Raises:
            ValueError: If line format is invalid
        """
        parts = line.strip().split("|")
        if len(parts) != 4:
            raise ValueError(
                f"Invalid bookmark format: expected 4 fields, got {len(parts)}",
            )

        name, url, description, tags = parts
        return cls(name=name, url=url, description=description, tags=tags)

    def matches_display_format(self, fields: list[str]) -> str:
        """Format bookmark for display according to specified fields.

        Args:
            fields: List of field names to display

        Returns:
            Formatted string with requested fields separated by pipes
        """
        field_map = {
            "name": self.name,
            "url": self.url,
            "description": self.description,
            "tags": self.tags,
        }

        display_values = []
        for field in fields:
            if field in field_map:
                display_values.append(field_map[field])
            else:
                display_values.append("")

        return "|".join(display_values)


class BookmarkManager:
    """Manages bookmark operations and file I/O.

    Handles reading, writing, and manipulating bookmark files while ensuring
    all invariants are maintained.
    """

    def __init__(self, bookmark_file: Path) -> None:
        """Initialize the bookmark manager.

        Args:
            bookmark_file: Path to the bookmark file
        """
        self.bookmark_file = bookmark_file

    def read_bookmarks(self) -> list[Bookmark]:
        """Read all bookmarks from the file.

        Returns:
            List of Bookmark objects

        Raises:
            FileNotFoundError: If bookmark file doesn't exist
            PermissionError: If bookmark file can't be read
        """
        if not self.bookmark_file.exists():
            return []

        bookmarks = []
        try:
            with open(self.bookmark_file, encoding="utf-8") as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line:  # Skip blank lines
                        continue

                    try:
                        bookmark = Bookmark.from_line(line)
                        bookmarks.append(bookmark)
                    except ValueError as e:
                        # Handle malformed entries gracefully - log and skip
                        print(
                            f"Warning: Skipping malformed bookmark on line {line_num}: {e}",
                        )
                        continue
        except PermissionError as e:
            raise PermissionError(
                f"Cannot read bookmark file {self.bookmark_file}: {e}",
            ) from e
        except OSError as e:
            raise OSError(
                f"Error reading bookmark file {self.bookmark_file}: {e}",
            ) from e

        return bookmarks

    def add_bookmark(self, bookmark: Bookmark) -> None:
        """Add a bookmark to the file.

        Args:
            bookmark: The bookmark to add

        Raises:
            PermissionError: If bookmark file can't be written
        """
        # Ensure parent directory exists
        self.bookmark_file.parent.mkdir(parents=True, exist_ok=True)

        try:
            with open(self.bookmark_file, "a", encoding="utf-8") as f:
                f.write(bookmark.to_line() + "\n")
        except PermissionError as e:
            raise PermissionError(
                f"Cannot write to bookmark file {self.bookmark_file}: {e}",
            ) from e
        except OSError as e:
            raise OSError(
                f"Error writing to bookmark file {self.bookmark_file}: {e}",
            ) from e

    def ensure_file_exists(self) -> None:
        """Ensure the bookmark file exists, creating it if necessary.

        Raises:
            PermissionError: If file can't be created
        """
        if not self.bookmark_file.exists():
            # Ensure parent directory exists
            self.bookmark_file.parent.mkdir(parents=True, exist_ok=True)

            try:
                self.bookmark_file.touch()
            except PermissionError as e:
                raise PermissionError(
                    f"Cannot create bookmark file {self.bookmark_file}: {e}",
                ) from e
            except OSError as e:
                raise OSError(
                    f"Error creating bookmark file {self.bookmark_file}: {e}",
                ) from e
