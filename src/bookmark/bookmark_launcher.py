"""Bookmark launch workflow with FZF selection and browser integration."""

import subprocess
import sys
import webbrowser
from pathlib import Path

from .file_manager import BookmarkFileManager
from .fzf_interface import FZFInterface
from .models import BookmarkManager


class BookmarkLauncher:
    """Handles the bookmark selection and launching workflow.

    Manages FZF-based bookmark selection and opening URLs in browsers
    with support for custom browser commands.
    """

    def __init__(
        self,
        file_manager: BookmarkFileManager,
        bookmark_file_path: Path | None = None,
        browser_command: str | None = None,
    ) -> None:
        """Initialize the bookmark launcher.

        Args:
            file_manager: File manager for handling bookmark operations
            bookmark_file_path: Optional specific bookmark file path
            browser_command: Optional browser command override
        """
        self.file_manager = file_manager
        self.fzf_interface = FZFInterface()
        self.browser_command = browser_command

        # Determine bookmark file to use
        if bookmark_file_path:
            self.bookmark_file = bookmark_file_path
        else:
            # Use config file to determine default
            config = file_manager.read_config()
            default_file = config.get("default_bookmark_file", "bookmarks.txt")
            self.bookmark_file = file_manager.get_bookmark_file_path(default_file)

        self.bookmark_manager = BookmarkManager(self.bookmark_file)

    def launch_bookmark(self) -> bool:
        """Run the interactive bookmark selection and launch workflow.

        Returns:
            True if bookmark was launched successfully, False otherwise
        """
        try:
            # Ensure base directory exists
            self.file_manager.ensure_base_directory()

            # Read bookmarks
            try:
                bookmarks = self.bookmark_manager.read_bookmarks()
            except (PermissionError, OSError) as e:
                print(f"Error reading bookmarks: {e}", file=sys.stderr)
                return False

            if not bookmarks:
                if self.bookmark_file.exists():
                    print("No bookmarks found in the file.")
                else:
                    print("No bookmark file found. Create some bookmarks first!")
                return False

            # Get display configuration
            config = self.file_manager.read_config()
            display_fields = config.get(
                "display_fields", ["name", "description", "url"],
            )

            # Format bookmarks for display
            bookmark_lines = []
            for bookmark in bookmarks:
                display_line = bookmark.matches_display_format(display_fields)
                bookmark_lines.append(display_line)

            # Use FZF to select bookmark
            selected_line = self.fzf_interface.select_bookmark(bookmark_lines)
            if not selected_line:
                return False

            # Find the corresponding bookmark
            selected_bookmark = None
            for i, line in enumerate(bookmark_lines):
                if line == selected_line:
                    selected_bookmark = bookmarks[i]
                    break

            if not selected_bookmark:
                print("Error: Could not find selected bookmark.", file=sys.stderr)
                return False

            # Launch the bookmark
            return self._launch_url(selected_bookmark.url)

        except (KeyboardInterrupt, EOFError):
            print("\nBookmark selection cancelled.")
            return False

    def _launch_url(self, url: str) -> bool:
        """Launch a URL in the appropriate browser.

        Args:
            url: URL to launch

        Returns:
            True if launch was successful, False otherwise
        """
        if not url:
            print("Error: No URL to launch.", file=sys.stderr)
            return False

        try:
            # Determine browser to use
            browser_cmd = self._get_browser_command()

            if browser_cmd:
                # Use custom browser command
                if isinstance(browser_cmd, str):
                    # Simple string command
                    subprocess.run([browser_cmd, url], check=True)
                else:
                    # List command
                    subprocess.run(browser_cmd + [url], check=True)
            else:
                # Use system default browser
                webbrowser.open(url)

            print(f"Launched: {url}")
            return True

        except subprocess.CalledProcessError as e:
            print(f"Error launching browser: {e}", file=sys.stderr)
            return False
        except Exception as e:
            print(f"Error opening URL: {e}", file=sys.stderr)
            return False

    def _get_browser_command(self) -> str | None:
        """Determine which browser command to use.

        Returns:
            Browser command string, or None for system default
        """
        # CLI option takes precedence
        if self.browser_command:
            return self.browser_command

        # Check config file
        config = self.file_manager.read_config()
        config_browser = config.get("browser")
        if config_browser:
            return config_browser

        # Use system default
        return None

    def list_bookmarks(self) -> bool:
        """List all bookmarks without launching.

        Returns:
            True if successful, False otherwise
        """
        try:
            # Ensure base directory exists
            self.file_manager.ensure_base_directory()

            # Read bookmarks
            try:
                bookmarks = self.bookmark_manager.read_bookmarks()
            except (PermissionError, OSError) as e:
                print(f"Error reading bookmarks: {e}", file=sys.stderr)
                return False

            if not bookmarks:
                print("No bookmarks found.")
                return True

            # Get display configuration
            config = self.file_manager.read_config()
            display_fields = config.get(
                "display_fields", ["name", "description", "url"],
            )

            # Print header
            header = "|".join(field.upper() for field in display_fields)
            print(header)
            print("-" * len(header))

            # Print bookmarks
            for bookmark in bookmarks:
                display_line = bookmark.matches_display_format(display_fields)
                print(display_line)

            return True

        except Exception as e:
            print(f"Error listing bookmarks: {e}", file=sys.stderr)
            return False
