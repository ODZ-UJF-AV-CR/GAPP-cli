# GAPP-cli agent notes

Python 3.9 CLI that uploads station GPS + MAVLink telemetry to a GAPP server.
Managed with `uv`; build backend is `uv_build` (see `pyproject.toml`), not setuptools/hatch.
`.python-version` pins 3.9; `pyproject.toml` sets `requires-python = ">=3.9"`.

## Commands

- Install deps:        `uv sync`
- Add dep:             `uv add <pkg>`
- Run from source:     `uv run gapp <config.toml>`
- Run as module:       `python3 -m gapp.cli <config.toml>`
- Install as tool:     `uv tool install .`  (then `gapp <config.toml>`)
- Tests:               `uv run pytest`  — `tests/` exists but is empty; `pytest` is in the `dev` dep group.

The CLI argument is a **TOML** file (see README.md for a full sample). There is no JSON config path.

No ruff/mypy config lives in the repo, and there are no CI workflows. Do not assume formatters, linters, or type checkers run automatically — running `ruff` or `mypy` will use defaults only.

## Architecture

`cli.main` (src/gapp/cli.py:10) orchestrates up to three `multiprocessing.Process` workers sharing one `multiprocessing.Queue`:

- Consumer: `run_telemetry_uploader` (src/gapp/uploader.py) — POSTs to `{server_url}/api/telemetry` with `httpx`.
- Producer: `run_gps_logger` (src/gapp/gps.py) — reads TPV packets from `gpsd`.
- Producer: `run_mavlink_logger` (src/gapp/mavlink.py) — reads `GPS_RAW_INT` via `pymavlink`.

Queue protocol: producers push `{"source": "gpsd"|"mavlink", "data": {...}}`. Stop signal sent to the uploader is a single `None` enqueued from `cli.main` on `KeyboardInterrupt`.

Config: TOML only. Defaults live in `gapp.config.DEFAULT_CONFIG` (src/gapp/config.py:9) and are deep-merged with the user file via `_deep_update`. `config.toml` is gitignored; the sample in README.md is the source of truth for shape.

## Conventions

- Absolute imports rooted at `gapp.` only — every existing module follows this. Do not introduce relative imports.
- Type hints expected on new code; existing code uses `typing.Dict/Optional/Any` for 3.9 compatibility — match that style rather than `dict[...]` / `X | None`.
- `snake_case` for funcs/vars, `PascalCase` for classes, leading `_` for module-private helpers (e.g. `_load_config_from_file`, `_deep_update`).
- Worker processes must exit cleanly on `KeyboardInterrupt`; fatal errors print to `sys.stderr` and call `sys.exit(1)` (pattern: src/gapp/gps.py:63-71).
- 4-space indent; no enforced line length.

## Known issues to be aware of when editing

- `src/gapp/uploader.py:72` references `payload['timestamp']` after a successful POST, but the payload only has `_time` (set at lines 38 and 45). This raises `KeyError` on every successful upload. Fix or work around if you touch this code path.
- `src/gapp/cli.py:40-49` starts the GPSD worker whenever `gpsd.enabled` is true, regardless of whether the uploader is running. The MAVLink branch (cli.py:57) correctly gates the queue with `queue_for_mav = telemetry_queue if server_url else None`; the GPSD branch does not, so when the uploader is disabled the queue fills with no consumer. Mirror the MAVLink gating pattern when modifying.
