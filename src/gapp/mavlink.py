import multiprocessing
import sys
from datetime import datetime, timezone
from typing import Optional
from pymavlink import mavutil

def run_mavlink_logger(
    connection_string: str,
    source_system: int,
    source_component: int,
    queue: Optional[multiprocessing.Queue] = None,
) -> None:
    """
    Connects to a MAVLink source and pushes GPS telemetry data to a queue.
    """
    print(f"MAVLink enabled - {connection_string} (System: {source_system}, Component: {source_component})")

    try:
        connection = mavutil.mavlink_connection(
            connection_string,
            source_system=source_system,
            source_component=source_component,
        )

        while True:
            msg = connection.recv_match(blocking=True, timeout=5) # type: ignore

            if msg:
                msg_type = msg.get_type()

                if msg_type == "GPS_RAW_INT":
                    data = {
                        "lat": msg.lat / 1.0e7,
                        "lon": msg.lon / 1.0e7,
                        "alt": msg.alt / 1000.0,
                        "time": datetime.now(timezone.utc)
                    }

                    if queue:
                        queue.put({"source": "mavlink", "data": data})

    except KeyboardInterrupt:
        print("\nStopping MAVLink logger.")
        sys.exit(0)
    except Exception as e:
        print(f"MAVLink Error: {e}", file=sys.stderr)
        sys.exit(1)
