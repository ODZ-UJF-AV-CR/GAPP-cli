import argparse
import json
import os
import sys
from typing import Any, Dict

DEFAULT_CONFIG = {
    "station_callsign": "",
    "gpsd": {
        "enabled": False,
        "host": "127.0.0.1",
        "port": 2947,
    },
    # Future nested configs for other modules (e.g., mavlink)
}


def _load_config_from_file(path: str) -> Dict[str, Any]:
    """Load configuration from a JSON file."""
    if not os.path.exists(path):
        return {}

    with open(path, "r") as f:
        return json.load(f)


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
    Parses CLI arguments and merges them with configuration file and defaults.
    Returns the final configuration dictionary.
    """
    parser = argparse.ArgumentParser(description="GAPP CLI Application")

    # Configuration file argument
    parser.add_argument(
        "-c", "--config", type=str, help="Path to JSON configuration file", default=None
    )

    # GPSD Configuration arguments
    parser.add_argument(
        "--gpsd-host",
        type=str,
        help="GPSD host address (default: 127.0.0.1)",
        default=None,
    )
    parser.add_argument(
        "--gpsd-port", type=int, help="GPSD port (default: 2947)", default=None
    )

    # GPSD Enable/Disable flags
    parser.add_argument(
        "--gpsd",
        action="store_true",
        dest="gpsd_enabled_flag",
        help="Enable GPSD logging",
        default=None,
    )
    parser.add_argument(
        "--no-gpsd",
        action="store_false",
        dest="gpsd_enabled_flag",
        help="Disable GPSD logging",
        default=None,
    )

    # Station Callsign argument
    parser.add_argument(
        "-sc",
        "--station-callsign",
        type=str,
        help="Station Call Sign",
        default=None,
    )

    args = parser.parse_args()

    # 1. Start with defaults (deep copy to avoid modifying global default)
    config = json.loads(json.dumps(DEFAULT_CONFIG))

    # 2. Load from config file if provided
    if args.config:
        try:
            file_config = _load_config_from_file(args.config)
            _deep_update(config, file_config)
        except Exception as e:
            print(f"Error loading config file: {e}", file=sys.stderr)
            sys.exit(1)

    # 3. Override with CLI arguments if they are set (not None)
    # We map flat CLI args to the nested structure
    if args.gpsd_host is not None:
        config["gpsd"]["host"] = args.gpsd_host

    if args.gpsd_port is not None:
        config["gpsd"]["port"] = args.gpsd_port

    if args.gpsd_enabled_flag is not None:
        config["gpsd"]["enabled"] = args.gpsd_enabled_flag

    if args.station_callsign is not None:
        config["station_callsign"] = args.station_callsign

    return config
