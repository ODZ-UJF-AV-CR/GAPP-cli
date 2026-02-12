import multiprocessing
import sys
from typing import Optional

from gpsdclient.client import GPSDClient


def run_gps_logger(
    host: str, port: int, queue: Optional[multiprocessing.Queue] = None
) -> None:
    """
    Connects to GPSD and streams TPV data to stdout.
    Optionally pushes data to a multiprocessing queue for telemetry upload.
    """
    print(f"Connecting to GPSD at {host}:{port}...")

    try:
        with GPSDClient(host=host, port=port) as client:
            for result in client.dict_stream(convert_datetime=True):
                # Filter for TPV (Time Position Velocity) reports which contain lat/lon/time
                if result.get("class") == "TPV" and queue is not None:
                    queue.put({"source": "gpsd", "data": result})

    except ConnectionRefusedError:
        print(f"Error: Could not connect to GPSD at {host}:{port}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nStopping GPSD logging.")
        sys.exit(0)
    except Exception as e:
        print(f"An error occurred: {e}", file=sys.stderr)
        sys.exit(1)
