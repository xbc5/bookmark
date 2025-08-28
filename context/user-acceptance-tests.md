# User Acceptance Tests - Bookmark Manager

## Test Suite 1: Installation and Directory Structure

### UAT-001: Directory Creation on First Use
**Given** the bookmark manager is run for the first time
**When** I execute any bookmark command
**Then** the `~/.bookmarks` directory should be created automatically
**And** the directory should have appropriate permissions

### UAT-002: Executable Installation
**Given** the bookmark manager is installed
**When** I type `bookmark` in any directory
**Then** the command should execute successfully
**And** I should see appropriate help or command options

## Test Suite 2: Bookmark File Format and Validation

### UAT-003: Valid Bookmark Entry Creation
**Given** I want to create a bookmark with all fields
**When** I provide name "My Test Site", URL "https://example.com", description "A test site", and tags "web,testing"
**Then** the bookmark should be saved as "My Test Site|https://example.com|A test site|web,testing"

### UAT-004: Bookmark with Empty Description
**Given** I want to create a bookmark without description
**When** I provide name "GitHub", URL "https://github.com", empty description, and tags "code,git"
**Then** the bookmark should be saved as "GitHub|https://github.com||code,git"

### UAT-005: Bookmark with Empty Tags
**Given** I want to create a bookmark without tags
**When** I provide name "News Site", URL "https://news.com", description "Daily news", and no tags
**Then** the bookmark should be saved as "News Site|https://news.com|Daily news|"

### UAT-006: Bookmark with Both Empty Description and Tags
**Given** I want to create a minimal bookmark
**When** I provide name "Simple Site", URL "https://simple.com", empty description, and no tags
**Then** the bookmark should be saved as "Simple Site|https://simple.com||"

### UAT-007: Name Validation - Pipe Character Rejection
**Given** I attempt to create a bookmark with pipe character in name
**When** I enter "My|Site" as the name
**Then** I should be reprompted for a valid name
**And** the pipe character should not be accepted

### UAT-008: Name Auto-Formatting to Title Case
**Given** I enter a name in various cases
**When** I provide "my test site" or "MY TEST SITE" or "mY tEsT sItE"
**Then** the name should be automatically converted to "My Test Site"

### UAT-009: Tag Normalization
**Given** I enter tags with mixed cases and extra spaces
**When** I provide " Testing , WEB , Code "
**Then** the tags should be normalized to "code,testing,web" (lowercase, sorted, no spaces)

### UAT-010: Duplicate Tag Removal
**Given** I enter duplicate tags
**When** I provide "web,testing,web,code,testing"
**Then** the tags should be deduplicated to "code,testing,web"

### UAT-011: Blank Lines Ignored
**Given** a bookmark file contains blank lines
**When** the file is read
**Then** blank lines should be ignored
**And** only non-empty lines should be processed as bookmarks

### UAT-012: Duplicate Bookmarks Allowed
**Given** I create a bookmark that already exists
**When** I add the same bookmark again
**Then** both entries should be saved in the file
**And** no error should occur

## Test Suite 3: Bookmark Creation Workflow

### UAT-013: Default Bookmark File Creation
**Given** no specific bookmark file is specified
**When** I create a bookmark
**Then** a default bookmark file should be used
**And** the file should be created if it doesn't exist

### UAT-014: Custom Bookmark File via CLI Flag
**Given** I specify a custom bookmark file via command line flag
**When** I create a bookmark
**Then** the bookmark should be saved to the specified file
**And** the file should be created if it doesn't exist

### UAT-015: Config File Fallback
**Given** no CLI flag is provided but a config file exists
**When** I create a bookmark
**Then** the bookmark file specified in config should be used

### UAT-016: Interactive Name Prompt
**Given** I'm creating a bookmark
**When** the system prompts for a name
**Then** I should be able to enter the bookmark name
**And** invalid names should trigger reprompting

### UAT-017: URL Input Acceptance
**Given** I'm prompted for a URL
**When** I enter any text (valid URL, invalid URL, or plain text)
**Then** the input should be accepted without validation

### UAT-018: Optional Description Prompt
**Given** I'm prompted for a description
**When** I press enter without typing anything
**Then** the description should be empty and the process should continue

### UAT-019: Tag Autocompletion
**Given** existing tags are available in `tags.txt`
**When** I'm prompted for tags
**Then** FZF-based autocompletion should show existing tags
**And** I should be able to select from existing tags

### UAT-020: New Tag Addition to Tags File
**Given** I enter a new tag that doesn't exist in `tags.txt`
**When** I complete the bookmark creation
**Then** the new tag should be added to `tags.txt`
**And** the tags should remain sorted alphabetically
**And** the tag should be in lowercase

## Test Suite 4: Bookmark Launch Workflow

### UAT-021: FZF Bookmark Selection
**Given** I have bookmarks in a file
**When** I launch the bookmark selection
**Then** FZF should display all bookmarks
**And** I should be able to search and select bookmarks

### UAT-022: Default Field Display
**Given** no custom display configuration exists
**When** bookmarks are displayed in FZF
**Then** the format should show "name|description|url"
**And** fields should be separated by pipe characters

### UAT-023: Custom Field Display via Config
**Given** `~/.bookmarks/config.yaml` specifies custom fields
**When** bookmarks are displayed
**Then** only the specified fields should be shown
**And** they should appear in the configured order

### UAT-024: Default Browser Launch
**Given** no browser is specified in CLI or config
**When** I select a bookmark
**Then** the URL should open in the system default browser

### UAT-025: CLI Browser Override
**Given** I specify a browser via CLI option
**When** I select a bookmark
**Then** the URL should open in the specified browser
**And** CLI option should override config settings

### UAT-026: Config File Browser Setting
**Given** a browser is specified in the config file
**And** no CLI browser option is provided
**When** I select a bookmark
**Then** the URL should open in the configured browser

## Test Suite 5: Tags Management

### UAT-027: Tags File Creation
**Given** no `tags.txt` file exists
**When** I create the first bookmark with tags
**Then** `tags.txt` should be created automatically
**And** it should contain the new tags

### UAT-028: Tags File Sorting
**Given** tags exist in various orders
**When** new tags are added
**Then** `tags.txt` should maintain alphabetical sorting

### UAT-029: Tag Independence from Bookmarks
**Given** a tag exists in bookmarks but not in `tags.txt`
**When** I use bookmarks functionality
**Then** the missing tag in `tags.txt` should not affect functionality
**And** autocompletion should work with available tags

### UAT-030: Case Insensitive Tag Handling
**Given** I enter tags in mixed case
**When** tags are processed
**Then** all tags should be stored in lowercase
**And** autocompletion should work regardless of input case

## Test Suite 6: Command Line Interface

### UAT-031: Create Subcommand
**Given** the bookmark manager is installed
**When** I run `bookmark create`
**Then** the bookmark creation workflow should start

### UAT-032: Launch Subcommand
**Given** bookmarks exist
**When** I run `bookmark launch` or similar command
**Then** the FZF selection interface should appear

### UAT-033: File Specification Flag
**Given** I want to use a specific bookmark file
**When** I run `bookmark --file custom.txt create`
**Then** the bookmark should be saved to `custom.txt`

### UAT-034: Help Information
**Given** I need help with commands
**When** I run `bookmark --help` or `bookmark -h`
**Then** usage information should be displayed

### UAT-035: Invalid Subcommand Handling
**Given** I run an invalid subcommand
**When** I execute `bookmark invalid-command`
**Then** an error message should be shown
**And** help information should be displayed

## Test Suite 7: File Operations and Error Handling

### UAT-036: File Creation on Demand
**Given** a specified bookmark file doesn't exist
**When** I create a bookmark
**Then** the file should be created automatically
**And** the bookmark should be saved successfully

### UAT-037: File Read Error Handling
**Given** a bookmark file exists but cannot be read (permissions issue)
**When** I try to launch bookmarks
**Then** an error message should be printed to stderr
**And** the program should exit gracefully

### UAT-038: File Write Error Handling
**Given** I cannot write to the bookmark file (permissions issue)
**When** I try to create a bookmark
**Then** an error message should be printed to stderr
**And** the program should exit gracefully

### UAT-039: Directory Permission Error
**Given** the `~/.bookmarks` directory cannot be created
**When** I run any bookmark command
**Then** an appropriate error message should be shown
**And** the program should exit gracefully

### UAT-040: Malformed Bookmark Entry Recovery
**Given** a bookmark file contains malformed entries
**When** the file is processed
**Then** malformed entries should be handled gracefully
**And** valid entries should still be processed

## Test Suite 8: Configuration Management

### UAT-041: Default Config Creation
**Given** no `config.yaml` exists
**When** bookmark launch is used
**Then** default display fields should be used ("name", "description", "url")

### UAT-042: Custom Display Fields
**Given** `config.yaml` specifies display fields as ["name", "url"]
**When** bookmarks are displayed
**Then** only name and URL should be shown
**And** description should be omitted

### UAT-043: Invalid Config Handling
**Given** `config.yaml` contains invalid YAML
**When** the config is read
**Then** default settings should be used
**And** an appropriate warning should be displayed

### UAT-044: Browser Configuration
**Given** `config.yaml` specifies a browser command
**When** bookmarks are launched
**Then** the configured browser should be used
**And** CLI options should override config settings

## Test Suite 9: Integration and End-to-End Scenarios

### UAT-045: Complete Bookmark Lifecycle
**Given** I'm starting with a fresh system
**When** I create a bookmark, launch it, and create another
**Then** all operations should work seamlessly
**And** all files should be created and maintained properly

### UAT-046: Multiple Bookmark Files
**Given** I use different bookmark files for different purposes
**When** I switch between files using CLI flags
**Then** each file should maintain its own bookmarks independently

### UAT-047: Large Bookmark File Performance
**Given** a bookmark file with hundreds of bookmarks
**When** I launch the bookmark selector
**Then** FZF should handle the large list efficiently
**And** search should work smoothly

### UAT-048: Cross-Platform Compatibility
**Given** the bookmark manager is installed on different systems
**When** I use the same bookmark files across systems
**Then** functionality should be consistent
**And** file formats should be compatible

### UAT-049: Unicode and Special Characters
**Given** I create bookmarks with unicode characters in names/descriptions
**When** I save and retrieve these bookmarks
**Then** unicode characters should be preserved correctly
**And** display should work properly

### UAT-050: Empty Bookmark File Handling
**Given** a bookmark file exists but is empty
**When** I try to launch bookmarks
**Then** an appropriate message should be shown
**And** no error should occur