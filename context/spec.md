# Bookmark Manager Specification

## Overview

This Python script manages bookmarks using simple, plain-text files. Bookmarks are created, stored, and launched via the command line interface, with tag-based autocompletion and FZF search.

## Installation and Directory Structure

- On installation or use, the script ensures that the `~/.bookmarks` directory exists.
- Bookmark files are stored as plain-text files (e.g., `~/.bookmarks/foo.txt`).
- Tags available for autocompletion are tracked in `~/.bookmarks/tags.txt`, sorted alphabetically.

## Bookmark File Format

- Each bookmark is a single line in the file.
- Format:  
  ```
  name|url|description|tags
  ```
- Fields:
    - **name**: Must not contain vertical bars (`|`). Input is reprompted until valid; the script enforces title case on names.
    - **url**: Any text is allowed.
    - **description**: Optional; if empty, leave the field empty.
    - **tags**: Comma-separated, lower-case. Optional; field remains empty if no tags provided. No duplicate tags or extra whitespace.
- Example (with descriptors filled):  
  ```
  My Example Bookmark|https://www.example.com|This is a test bookmark.|testing,example
  ```
  Example (with description and tags empty):  
  ```
  My Second Bookmark|https://another.com||
  ```
- The final pipe (`|`) delimiter **is always present** even if description or tags are empty.
- **Blank lines are ignored.**
- **No comments are allowed.**
- **Duplicate bookmarks are permitted.**

## Invariants Enforcement

- All specified invariants (field count, no vertical bars in name, non-duplicate trimmed tags in lower-case, name title case) are enforced automatically and silently corrected during input.
- If a bookmark entry is malformed (too many/little fields), this reflects a programmer error and should not occur.

## Tags Autocompletion

- Tags from `~/.bookmarks/tags.txt` are used only for autocompletion; they do not control what tags actually exist in bookmarks. If a tag is used in a bookmark but not in the tags file, autocompletion is unaffected.
- When a user enters a new tag, it is added to the file in lower-case, sorted order with no duplicates.

## Bookmark Creation Workflow

1. Ensure the target bookmark file exists (using a command line flag for the file; otherwise, fallback to a config file or use a default name).
2. Prompt the user for the bookmark's name (reprompt until valid, then apply title case).
3. Prompt for the URL (accept any text).
4. Prompt for an optional description (empty allowed).
5. Prompt for optional tags (FZF-based autocompletion, lower-case, comma-separated, no duplicates).
6. Enforce all invariants, correcting them silently.
7. Append the bookmark entry to the specified file.

## Bookmark Launch Workflow

1. Use FZF to present all bookmarks in the chosen file.
2. Display fields according to a list specified in `~/.bookmarks/config.yaml` (`name`, `description`, `url` by default) using a pipe (`|`) separator.
3. Upon choosing a bookmark, open it in the user’s default browser or, if a browser command is specified via CLI or config file, use that.
   - The CLI option takes precedence over config.
   - If neither is specified, the system default browser is used.

## Command Line Interface

- Provides subcommands for creating and launching bookmarks, and for specifying which bookmarks file to use.
- All prompts provide FZF-based autocompletion where appropriate.
- No CLI support for editing or deleting bookmarks or tags; these are managed by manual file edits.

## Files Behavior

- All files are plain-text.
- Files (`tags.txt`, bookmarks files) are created if not present.
- Blank lines in bookmarks files are ignored.
- Every non-empty line in a bookmarks file is a bookmark entry.
- No support for comments, encryption, export/import, or categories.
- On file read/write errors, print an error message to stderr and exit.
