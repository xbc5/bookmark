## Meta

- The project is called **bookmark**.
- After installation, the script should be executable from any location.
- I want to be able to run the script simply by typing `bookmark` in the terminal.

## Code Style

- Write clean, direct code following best practices for readability.
- Use clear comments to indicate what each section of code does and why it's necessary.
- Include type hints throughout the codebase.
- Format all code with **Black**.
- Use **Ruff** for linting.

## Dependencies

- Use **UV** for dependency management.
- You can install and use any dependency that you wish.
- Use dependencies if it reduces code duplication or improves readability.
- Do not use different versions of the same dependency.
- Do not use different dependencies to achieve the same goal.

## Testing

- Write code that is easy to test.
- Use **pytest** for testing.
- Where possible, test against real files instead of using mocks, utilizing pytest’s built-in fixtures.
- Ensure comprehensive unit test coverage; implement enough integration tests to ensure components work together correctly.

## Project Structure

- Organize code into packages, using `__init__.py` files to provide the public interface.

Example structure:

```
project/
├── .venv/
├── pyproject.toml
├── uv.lock
├── README.md
├── main.py
├── src/
│   └── bookmark/
│       ├── __init__.py
│       └── utils.py
└── tests/
    └── test_utils.py
```
