## Meta

- The project is named **bookmark**.
- After installation, the script must be executable from any directory.
- The script should be runnable by typing `bookmark` in the terminal.

## Code Style

- Write clean, readable code that follows best practices.
- Add clear comments to describe what each section does and why it exists.
- Use type hints throughout the code.
- Format all code with **Black**.
- Lint the code using **Ruff**.

## Documentation

- Write clear and concise documentation for every function and class.
- Use docstrings to explain the purpose, parameters, and return values of functions.
- Use a first-person, imperative tone in documentation.
- Clearly state the purpose and behavior for each function and class.

## Dependencies

- Manage dependencies with **UV**.
- Install and use any dependencies as needed.
- Use dependencies to reduce code duplication and improve readability.
- Avoid using multiple versions of the same dependency.
- Do not use different dependencies to serve the same purpose.

## Testing

- Write code that is straightforward to test.
- Use **pytest** for all testing.
- Prefer testing with real files using pytest's fixtures over mocks when possible.
- Achieve thorough unit test coverage; add integration tests to validate interactions between components.

## Project Structure

- Structure the code into packages, using `__init__.py` files to define the public interface.

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
