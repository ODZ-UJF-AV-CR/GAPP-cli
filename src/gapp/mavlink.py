import multiprocessing
import sys
from datetime import datetime, timezone
from typing import Optional
from pymavlink import mavutil

from gapp import sounds

def run_mavlink_logger(
    connection_string: str,
    source_system: int,
    source_component: int,
    queue: Optional[multiprocessing.Queue] = None,
    baud: int = 115200,
    print_packets: bool = False,
) -> None:
    """
    Connects to a MAVLink source and pushes GPS telemetry data to a queue.
    """
    print(f"MAVLink enabled - {connection_string} (System: {source_system}, Component: {source_component})")

    try:
        connection = mavutil.mavlink_connection(
            connection_string,
            baud=baud,
            source_system=source_system,
            source_component=source_component,
        )

        HIGHLIGHT_TYPES = {"ALTITUDE", "GPS_RAW_INT"}
        ANSI_YELLOW = "\033[1;33m"
        ANSI_RESET = "\033[0m"

        while True:
            msg = connection.recv_match(blocking=True, timeout=5) # type: ignore

            if msg:
                msg_type = msg.get_type()
                if print_packets and msg_type != "BAD_DATA":
                    if msg_type in HIGHLIGHT_TYPES:
                        print(f"\a{ANSI_YELLOW}MAVLink packet [{msg_type}] {msg}{ANSI_RESET}", flush=True)
                    else:
                        print(f"MAVLink packet [{msg_type}] {msg}", flush=True)

                if msg_type == "HEARTBEAT":
                    # Heartbeats are typically 1 Hz, throttle the cue.
                    sounds.play("heartbeat", min_interval=10.0)

                if msg_type == "TUNNEL":
                    # Custom data payload arrival.
                    sounds.play("data", min_interval=1.0)

                if msg_type == "GPS_RAW_INT":
                    data = {
                        "lat": msg.lat / 1.0e7,
                        "lon": msg.lon / 1.0e7,
                        "alt": msg.alt / 1000.0,
                        "time": datetime.now(timezone.utc)
                    }

                    sounds.play("position", min_interval=5.0)

                    if queue:
                        queue.put({"source": "mavlink", "data": data})

    except KeyboardInterrupt:
        print("\nStopping MAVLink logger.")
        sys.exit(0)
    except Exception as e:
        print(f"MAVLink Error: {e}", file=sys.stderr)
        sys.exit(1)
