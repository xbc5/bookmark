"""Bookmark creation workflow with interactive prompts."""

import sys
from pathlib import Path

from .file_manager import BookmarkFileManager
from .fzf_interface import FZFInterface, TagInput
from .models import Bookmark, BookmarkManager


class BookmarkCreator:
    """Handles the interactive bookmark creation workflow.

    Manages the complete workflow for creating bookmarks with validation,
    user prompts, and tag management.
    """

    def __init__(
        self,
        file_manager: BookmarkFileManager,
        bookmark_file_path: Path | None = None,
    ) -> None:
        """Initialize the bookmark creator.

        Args:
            file_manager: File manager for handling bookmark operations
            bookmark_file_path: Optional specific bookmark file path
        """
        self.file_manager = file_manager
        self.fzf_interface = FZFInterface()
        self.tag_input = TagInput(self.fzf_interface)

        # Determine bookmark file to use
        if bookmark_file_path:
            self.bookmark_file = bookmark_file_path
        else:
            # Use config file to determine default
            config = file_manager.read_config()
            default_file = config.get("default_bookmark_file", "bookmarks.txt")
            self.bookmark_file = file_manager.get_bookmark_file_path(default_file)

        self.bookmark_manager = BookmarkManager(self.bookmark_file)

    def create_bookmark(self) -> bool:
        """Run the interactive bookmark creation workflow.

        Returns:
            True if bookmark was created successfully, False otherwise
        """
        try:
            # Ensure base directory and bookmark file exist
            self.file_manager.ensure_base_directory()
            self.bookmark_manager.ensure_file_exists()

            # Get bookmark details from user
            name = self._get_bookmark_name()
            if not name:
                return False

            url = self._get_bookmark_url()
            description = self._get_bookmark_description()
            tags = self._get_bookmark_tags()

            # Create and validate bookmark
            try:
                bookmark = Bookmark(
                    name=name, url=url, description=description, tags=tags,
                )
            except ValueError as e:
                print(f"Error creating bookmark: {e}", file=sys.stderr)
                return False

            # Save bookmark
            try:
                self.bookmark_manager.add_bookmark(bookmark)
                print(f"Bookmark '{bookmark.name}' added successfully!")

                # Update tags file if new tags were added
                if bookmark.tags:
                    tag_list = [tag.strip() for tag in bookmark.tags.split(",")]
                    self.file_manager.update_tags(tag_list)

                return True

            except (PermissionError, OSError) as e:
                print(f"Error saving bookmark: {e}", file=sys.stderr)
                return False

        except (KeyboardInterrupt, EOFError):
            print("\nBookmark creation cancelled.")
            return False

    def _get_bookmark_name(self) -> str | None:
        """Get a valid bookmark name from user input.

        Returns:
            Valid bookmark name, or None if cancelled
        """
        while True:
            try:
                name = input("Enter bookmark name: ").strip()
                if not name:
                    print("Name cannot be empty.")
                    continue

                if "|" in name:
                    print("Name cannot contain pipe characters (|). Please try again.")
                    continue

                return name

            except (KeyboardInterrupt, EOFError):
                return None

    def _get_bookmark_url(self) -> str:
        """Get bookmark URL from user input.

        Returns:
            URL string (any text is allowed per spec)
        """
        try:
            return input("Enter URL: ").strip()
        except (KeyboardInterrupt, EOFError):
            return ""

    def _get_bookmark_description(self) -> str:
        """Get optional bookmark description from user input.

        Returns:
            Description string (empty allowed)
        """
        try:
            return input("Enter description (optional): ").strip()
        except (KeyboardInterrupt, EOFError):
            return ""

    def _get_bookmark_tags(self) -> str:
        """Get bookmark tags from user input with autocompletion.

        Returns:
            Comma-separated tags string
        """
        try:
            available_tags = self.file_manager.read_tags()
            return self.tag_input.get_tags_input(available_tags)
        except (KeyboardInterrupt, EOFError):
            return ""
