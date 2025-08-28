"""Command line interface for the bookmark manager."""

import argparse
import sys

from .bookmark_creator import BookmarkCreator
from .bookmark_launcher import BookmarkLauncher
from .file_manager import BookmarkFileManager


def create_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser.

    Returns:
        Configured ArgumentParser instance
    """
    parser = argparse.ArgumentParser(
        prog="bookmark",
        description="A command-line bookmark manager using plain text files with FZF integration",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  bookmark create                    # Create a new bookmark interactively
  bookmark launch                    # Launch a bookmark using FZF selection
  bookmark list                      # List all bookmarks
  bookmark --file work.txt create    # Create bookmark in specific file
  bookmark --browser firefox launch # Launch with specific browser

The bookmark manager stores bookmarks in ~/.bookmarks/ by default.
Each bookmark is stored as: name|url|description|tags
        """,
    )

    # Global options
    parser.add_argument(
        "--file",
        "-f",
        type=str,
        help="Specify bookmark file to use (default: bookmarks.txt)",
    )

    parser.add_argument(
        "--browser",
        "-b",
        type=str,
        help="Browser command to use for launching bookmarks",
    )

    parser.add_argument("--version", "-v", action="version", version="%(prog)s 0.1.0")

    # Subcommands
    subparsers = parser.add_subparsers(
        dest="command", help="Available commands", metavar="COMMAND",
    )

    # Create subcommand
    create_parser = subparsers.add_parser(
        "create",
        help="Create a new bookmark interactively",
        description="Create a new bookmark with interactive prompts",
    )

    # Launch subcommand
    launch_parser = subparsers.add_parser(
        "launch",
        help="Launch a bookmark using FZF selection",
        description="Select and launch a bookmark using FZF",
    )

    # List subcommand
    list_parser = subparsers.add_parser(
        "list",
        help="List all bookmarks",
        description="Display all bookmarks in the current file",
    )

    return parser


def main() -> None:
    """Main entry point for the bookmark CLI."""
    parser = create_parser()
    args = parser.parse_args()

    # If no command specified, show help
    if not args.command:
        parser.print_help()
        sys.exit(1)

    try:
        # Initialize file manager
        file_manager = BookmarkFileManager()

        # Determine bookmark file path if specified
        bookmark_file_path = None
        if args.file:
            bookmark_file_path = file_manager.get_bookmark_file_path(args.file)

        # Handle commands
        if args.command == "create":
            creator = BookmarkCreator(file_manager, bookmark_file_path)
            success = creator.create_bookmark()
            sys.exit(0 if success else 1)

        elif args.command == "launch":
            launcher = BookmarkLauncher(file_manager, bookmark_file_path, args.browser)
            success = launcher.launch_bookmark()
            sys.exit(0 if success else 1)

        elif args.command == "list":
            launcher = BookmarkLauncher(file_manager, bookmark_file_path)
            success = launcher.list_bookmarks()
            sys.exit(0 if success else 1)

        else:
            print(f"Error: Unknown command '{args.command}'", file=sys.stderr)
            parser.print_help()
            sys.exit(1)

    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
