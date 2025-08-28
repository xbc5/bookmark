"""FZF integration for bookmark selection and tag autocompletion."""

import subprocess
import sys


class FZFInterface:
    """Provides FZF integration for interactive selection.

    Handles both bookmark selection and tag autocompletion using FZF,
    ensuring a smooth user experience for finding and selecting items.
    """

    def __init__(self) -> None:
        """Initialize the FZF interface."""
        self._check_fzf_availability()

    def _check_fzf_availability(self) -> None:
        """Check if FZF is available on the system.

        Raises:
            SystemExit: If FZF is not available
        """
        try:
            subprocess.run(
                ["fzf", "--version"], capture_output=True, check=True, timeout=5,
            )
        except (
            subprocess.CalledProcessError,
            FileNotFoundError,
            subprocess.TimeoutExpired,
        ):
            print(
                "Error: FZF is required but not found. Please install FZF.",
                file=sys.stderr,
            )
            print(
                "Visit: https://github.com/junegunn/fzf#installation", file=sys.stderr,
            )
            sys.exit(1)

    def select_bookmark(
        self, bookmark_lines: list[str], prompt: str = "Select bookmark: ",
    ) -> str | None:
        """Use FZF to select a bookmark from a list.

        Args:
            bookmark_lines: List of formatted bookmark lines for display
            prompt: Prompt text for FZF

        Returns:
            Selected bookmark line, or None if cancelled
        """
        if not bookmark_lines:
            print("No bookmarks available.")
            return None

        try:
            # Create FZF process
            fzf_cmd = [
                "fzf",
                "--prompt",
                prompt,
                "--height",
                "40%",
                "--reverse",
                "--border",
                "--info=inline",
            ]

            process = subprocess.Popen(
                fzf_cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8",
            )

            # Send bookmark lines to FZF
            input_data = "\n".join(bookmark_lines)
            stdout, stderr = process.communicate(input=input_data)

            if process.returncode == 0:
                return stdout.strip()
            if process.returncode == 130:  # Ctrl+C
                return None
            print(f"FZF error: {stderr}", file=sys.stderr)
            return None

        except Exception as e:
            print(f"Error running FZF: {e}", file=sys.stderr)
            return None

    def input_with_completion(
        self, prompt: str, completion_items: list[str], allow_multiple: bool = True,
    ) -> str:
        """Get input with FZF-based autocompletion.

        Args:
            prompt: Prompt text to display
            completion_items: List of items for autocompletion
            allow_multiple: Whether to allow multiple comma-separated selections

        Returns:
            User input string
        """
        print(f"{prompt}", end="", flush=True)

        if not completion_items:
            # No completion items, just get regular input
            return input()

        try:
            # For now, implement basic input with fallback
            # In a full implementation, this could use a more sophisticated approach
            # with FZF for tag completion, but for initial implementation we'll use
            # simple input with a hint about available tags
            if completion_items:
                print(
                    f" (available: {', '.join(completion_items[:5])}{'...' if len(completion_items) > 5 else ''})",
                )
                print(prompt, end="", flush=True)

            return input()

        except (KeyboardInterrupt, EOFError):
            return ""

    def select_tags(self, available_tags: list[str]) -> list[str]:
        """Select multiple tags using FZF.

        Args:
            available_tags: List of available tags for selection

        Returns:
            List of selected tags
        """
        if not available_tags:
            return []

        try:
            # Use FZF for multi-select
            fzf_cmd = [
                "fzf",
                "--multi",
                "--prompt",
                "Select tags (TAB to select multiple): ",
                "--height",
                "40%",
                "--reverse",
                "--border",
                "--info=inline",
            ]

            process = subprocess.Popen(
                fzf_cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8",
            )

            # Send tags to FZF
            input_data = "\n".join(available_tags)
            stdout, stderr = process.communicate(input=input_data)

            if process.returncode == 0:
                selected = [
                    tag.strip() for tag in stdout.strip().split("\n") if tag.strip()
                ]
                return selected
            return []

        except Exception as e:
            print(f"Error selecting tags: {e}", file=sys.stderr)
            return []


class TagInput:
    """Handles tag input with autocompletion and validation."""

    def __init__(self, fzf_interface: FZFInterface) -> None:
        """Initialize tag input handler.

        Args:
            fzf_interface: FZF interface for selections
        """
        self.fzf_interface = fzf_interface

    def get_tags_input(self, available_tags: list[str]) -> str:
        """Get tags input from user with autocompletion support.

        Args:
            available_tags: List of available tags for autocompletion

        Returns:
            Comma-separated tags string
        """
        print(
            "Enter tags (comma-separated, or press Enter to select from available): ",
            end="",
            flush=True,
        )

        user_input = input().strip()

        if not user_input and available_tags:
            # User pressed Enter without input, show FZF selection
            selected_tags = self.fzf_interface.select_tags(available_tags)
            return ",".join(selected_tags)

        return user_input
