import multiprocessing
import sys
import time
from typing import Any, Dict

import httpx


def run_telemetry_uploader(
    server_url: str, queue: multiprocessing.Queue, station_callsign: str, mavlink_callsign: str
) -> None:
    """
    Process that consumes telemetry data from the queue and uploads it to the server.
    """
    api_endpoint = f"{server_url}/api/telemetry"

    print(f"Telemetry uploader enabled - {api_endpoint}")

    with httpx.Client() as client:
        while True:
            try:
                item: Dict[str, Any] = queue.get()

                # Check for stop signal (None)
                if item is None:
                    break

                source = item.get("source", "unknown")
                data = item.get("data", {})

                payload = {}

                if source == "gpsd":
                    payload["callsign"] = station_callsign
                    payload["latitude"] = data.get("lat")
                    payload["longitude"] = data.get("lon")
                    payload["altitude"] = data.get("alt", 0.0)
                    payload["timestamp"] = data.get("time").isoformat()

                if source == "mavlink":
                    payload["callsign"] = mavlink_callsign
                    payload["latitude"] = data.get("lat")
                    payload["longitude"] = data.get("lon")
                    payload["altitude"] = data.get("alt", 0.0)
                    payload["timestamp"] = data.get("time").isoformat()
                    # Add extra MAVLink fields
                    for k, v in data.items():
                        if k not in ["lat", "lon", "alt", "time"]:
                            payload[k] = v

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
                    print(
                        f"Skipping incomplete telemetry packet from {source}: {payload}",
                        file=sys.stderr,
                    )
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
