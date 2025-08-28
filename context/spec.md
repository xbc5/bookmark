# Bookmark Manager Specification

## Overview

This project is a Python script that manages bookmarks by reading files located in `~/.bookmarks/foo.txt` and launching the selected bookmark in a preferred browser. The script is installable, and upon installation, it ensures the `~/.bookmarks` directory exists, creating it if necessary.

## Bookmark Creation and Storage

- Users can create bookmark files within the `~/.bookmarks` directory using a command line option.
- The script allows users to create a bookmark file (e.g., `~/.bookmarks/foo.txt`) if it does not already exist.
- Each bookmark is stored as one line in the file, using the following pipe-delimited format:  
  ```
  name|url|description|tags
  ```

#### Example

```
Example\| An example website|https://www.example.com|This website is an example that I often use for testing.|foo,bar,baz|
```

### Bookmark File Format Invariants

- **Tags** are comma-separated.
- **Description**:
  - Begins with a capital letter.
  - Ends with a period.
- **Name**:
  - Prefixed by a category: `"Category \| An example website"`.
  - Uses title case for both category and following text.
  - Never ends in a period.
  - Vertical bars in the name are escaped with a backslash (`\|`).

The program should not crash upon invariant violation. Instead, it should automatically correct the issues.

## Category and Tag Management

### Category Tracking

- Categories are tracked in a separate file: `~/.bookmarks/categories.txt`.
- When creating a new bookmark, the script uses the category as a prefix for the bookmark’s name.
- If the category file does not exist, it will be created.
- Categories are ordered alphabetically.

### Tag Tracking

- Tags are tracked in `~/.bookmarks/tags.txt`, with one tag per line.
- If the tag file does not exist, it will be created.
- Tags are ordered alphabetically.

## Bookmark Creation Workflow

When creating a new bookmark, the following steps occur:

1. Create the category file if it does not exist.
2. Create the bookmark file (`~/.bookmarks/foo.txt`) if it does not exist.
3. Prompt the user for the bookmark's URL.
4. Prompt the user for a category (using FZF for fuzzy selection).
   - If the entered category does not exist, it is added and used.
5. Prompt the user for the bookmark name.
6. Prompt for an optional description (Return skips this step).
7. Prompt for optional tags (Return skips this step, tags selected via fuzzy search from the tag file).

## Bookmark Selection and Launch

- The script uses FZF (fuzzy finder) to allow rapid bookmark selection from the bookmark file.
- The selection interface is flat and non-hierarchical; users search directly within the entire bookmark file.
- Upon selection, the script launches the bookmark in the user's default browser, or uses a specified command pattern (e.g., `browsername [options] %s`).

## Command Line Interface

- The script provides a clean, user-friendly CLI for both creating and launching bookmarks.
- All prompts (category, name, description, tags) utilize FZF for fuzzy searching over existing entries, facilitating fast and efficient input.

