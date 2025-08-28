"""Bookmark manager package for managing bookmarks with plain text files."""

from .cli import main
from .models import Bookmark, BookmarkManager

__all__ = ["Bookmark", "BookmarkManager", "main"]
