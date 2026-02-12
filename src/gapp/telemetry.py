import multiprocessing
import sys
import time
from typing import Any, Dict

import httpx

def run_telemetry_uploader(
    server_url: str, queue: multiprocessing.Queue, station_callsign: str
) -> None:
    """
    Process that consumes telemetry data from the queue and uploads it to the server.
    """
    print(f"Telemetry uploader started. Target: {server_url}")

    # Ensure URL ends with /api/telemetry if not provided
    # The user said "server_url" config, but implied it's the base URL or the full URL?
    # Usually server_url is base. I'll robustly handle it.
    api_endpoint = server_url.rstrip("/")
    if not api_endpoint.endswith("/api/telemetry"):
        api_endpoint += "/api/telemetry"

    with httpx.Client() as client:
        while True:
            try:
                # Get data from queue
                item: Dict[str, Any] = queue.get()

                # Check for stop signal (None)
                if item is None:
                    break

                source = item.get("source", "unknown")
                data = item.get("data", {})

                # Normalize data based on source
                payload = {}

                if source == "gpsd":
                    # Extract GPSD specific fields
                    # GPSD TPV objects have lat, lon, alt, time (ISO8601)
                    payload["callsign"] = station_callsign
                    payload["latitude"] = data.get("lat")
                    payload["longitude"] = data.get("lon")
                    payload["altitude"] = data.get(
                        "alt", 0.0
                    )  # Default to 0 if missing
                    payload["timestamp"] = data.get("time").isoformat()

                # Validate required fields
                if not all(
                    k in payload and payload[k] is not None
                    for k in [
                        "callsign",
                        "latitude",
                        "longitude",
                        "altitude",
                        "timestamp",
                    ]
                ):
                    # Skip invalid packets
                    print(f"Skipping incomplete telemetry packet from {source}: {payload}", file=sys.stderr)
                    continue

                # Upload
                try:
                    response = client.post(api_endpoint, json=payload, timeout=5.0)
                    response.raise_for_status()
                    print(f"Uploaded telemetry: {payload['timestamp']}")
                except httpx.HTTPError as e:
                    print(e)
                    print(f"Failed to upload telemetry: {e}", file=sys.stderr)

            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Telemetry uploader error: {e}", file=sys.stderr)
                # Don't crash the loop on transient errors
                time.sleep(1)
