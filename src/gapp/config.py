import argparse
import copy
import os
import sys
from typing import Any, Dict

import toml

DEFAULT_CONFIG = {
    "uploader": {
        "enabled": True,
        "station_callsign": "",
        "server_url": "",
    },
    "gpsd": {
        "enabled": True,
        "host": "127.0.0.1",
        "port": 2947,
        "interval": 15,  # Interval in seconds
    },
}


def _load_config_from_file(path: str) -> Dict[str, Any]:
    """Load configuration from a TOML file."""
    if not os.path.exists(path):
        return {}

    with open(path, "r") as f:
        return toml.load(f)


def _deep_update(base_dict: Dict[str, Any], update_dict: Dict[str, Any]) -> None:
    """Recursively update a dictionary."""
    for key, value in update_dict.items():
        if (
            key in base_dict
            and isinstance(base_dict[key], dict)
            and isinstance(value, dict)
        ):
            _deep_update(base_dict[key], value)
        else:
            base_dict[key] = value


def get_config() -> Dict[str, Any]:
    """
    Parses CLI arguments (config file path only) and merges file config with defaults.
    Returns the final configuration dictionary.
    """
    parser = argparse.ArgumentParser(
        description="GAPP - cli utility to upload telemetry to gapp server"
    )

    parser.add_argument("config_path", type=str, help="Path to TOML configuration file")

    args = parser.parse_args()

    config = copy.deepcopy(DEFAULT_CONFIG)

    if not os.path.exists(args.config_path):
        print(
            f"Error: Configuration file not found at '{args.config_path}'",
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        file_config = _load_config_from_file(args.config_path)
        _deep_update(config, file_config)
    except Exception as e:
        print(f"Error loading config file: {e}", file=sys.stderr)
        sys.exit(1)

    return config
