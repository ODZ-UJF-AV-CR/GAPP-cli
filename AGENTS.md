# GAPP-cli Development Guide

This repository contains the GAPP command-line interface for uploading station position and telemetry data.
The project uses Python (>=3.9) and `uv` for dependency management and packaging.

## 1. Build, Run, and Test Commands

### Environment Setup
- **Install Dependencies:**
  ```bash
  uv sync
  ```
- **Add Dependency:**
  ```bash
  uv add <package_name>
  ```

### Running the Application
The application entry point is `gapp.cli:main`. It requires a configuration file argument.
- **Run directly:**
  ```bash
  uv run gapp config.json
  ```
- **Run as module:**
  ```bash
  python3 -m gapp.cli config.json
  ```

### Testing
Currently, there are no tests. When adding tests:
- **Location:** Create a `tests/` directory at the project root.
- **Framework:** Use `pytest`.
- **Command:**
  ```bash
  uv run pytest
  ```
- **Run Single Test:**
  ```bash
  uv run pytest tests/test_file.py::test_function_name
  ```

### Linting and Formatting
The project does not enforce strict linting rules yet, but standard Python tools are recommended.
- **Lint:**
  ```bash
  uv run ruff check .
  ```
- **Format:**
  ```bash
  uv run ruff format .
  ```
- **Type Check:**
  ```bash
  uv run mypy src/
  ```

---

## 2. Code Style Guidelines

### General Principles
- **Clarity:** Code should be self-documenting where possible.
- **Consistency:** Follow existing patterns in the codebase.
- **Simplicity:** Prefer simple, readable solutions over complex ones.

### Formatting & Structure
- **Indentation:** Use 4 spaces.
- **Line Length:** Aim for 88-100 characters (compatible with `black`/`ruff`).
- **Imports:** Group imports in the following order:
  1.  Standard Library (`import os`, `import sys`)
  2.  Third-party Libraries (`from gpsdclient import ...`)
  3.  Local Application Imports (`from gapp.config import ...`)
  Use absolute imports for local modules (e.g., `from gapp.gps import ...` instead of `from .gps import ...`).

### Naming Conventions
- **Variables/Functions:** `snake_case` (e.g., `run_gps_logger`, `server_url`).
- **Classes:** `PascalCase` (e.g., `GpsLogger`).
- **Constants:** `UPPER_CASE` (e.g., `DEFAULT_CONFIG`).
- **Private Members:** Prefix with underscore `_` (e.g., `_load_config_from_file`).

### Type Hinting
- **Mandatory:** Use type hints for function arguments and return values.
- **Imports:** Use `typing` module (e.g., `List`, `Dict`, `Optional`, `Any`) for compatibility with older Python versions if necessary, or standard collection types for Python 3.9+.
- **Example:**
  ```python
  def get_data(source: str, timeout: int = 10) -> Dict[str, Any]:
      ...
  ```

### Error Handling
- **Explicit Exceptions:** Catch specific exceptions (e.g., `ConnectionRefusedError`, `FileNotFoundError`) rather than bare `except:`.
- **Graceful Exit:** For critical errors in CLI tools, print a clear message to `sys.stderr` and exit with a non-zero status code (`sys.exit(1)`).
- **Cleanup:** Ensure resources (like subprocesses) are cleaned up properly, especially on `KeyboardInterrupt`.

### Documentation
- **Docstrings:** Use docstrings for all public modules, classes, and functions.
- **Style:** Google style is preferred (Description, Args, Returns, Raises).
- **Example:**
  ```python
  def connect(host: str, port: int) -> None:
      """
      Connects to the server.

      Args:
          host: The server hostname.
          port: The server port.

      Raises:
          ConnectionError: If connection fails.
      """
  ```

### Concurrency
- The application uses `multiprocessing` for concurrent modules (GPS logger, Telemetry uploader).
- Ensure processes are properly terminated and joined on exit.
- use `multiprocessing.Queue` for inter-process communication.
