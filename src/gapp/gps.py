import multiprocessing
import sys
import time
from typing import Optional
from gpsdclient.client import GPSDClient


def run_gps_logger(
    host: str,
    port: int,
    interval: int,
    queue: Optional[multiprocessing.Queue] = None,
) -> None:
    """
    Connects to GPSD and streams TPV data to stdout.
    Optionally pushes data to a multiprocessing queue for telemetry upload.
    """
    print(f"GPSD enabled - {host}:{port}")

    try:
        with GPSDClient(host=host, port=port) as client:
            last_log_time = 0.0

            for packet in client.dict_stream(filter=["TPV"]):
                current_time = time.time()

                # Rate limiting based on interval
                if current_time - last_log_time < interval:
                    continue

                last_log_time = current_time

                try:
                    # Check mode: 0=no mode, 1=no fix, 2=2D fix, 3=3D fix
                    mode = packet.get("mode", 0)

                    if mode >= 2:
                        lat = packet.get("lat")
                        lon = packet.get("lon")
                        time_utc = packet.get("time")

                        # Altitude is only available in 3D mode (mode >= 3)
                        alt = packet.get("alt", 0.0) if mode >= 3 else 0.0

                        print(
                            f"GPS Fix: Lat={lat}, Lon={lon}, Alt={alt}, Time={time_utc}"
                        )

                        if queue:
                            data = {
                                "lat": lat,
                                "lon": lon,
                                "alt": alt,
                                "time": time_utc,
                            }
                            queue.put({"source": "gpsd", "data": data})
                    else:
                        print("GPS: No fix")

                except Exception as e:
                    print(f"Error processing GPS packet: {e}", file=sys.stderr)

    except ConnectionRefusedError:
        print(f"Error: Could not connect to GPSD at {host}:{port}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nStopping GPSD logging.")
        sys.exit(0)
    except Exception as e:
        print(f"An error occurred: {e}", file=sys.stderr)
        sys.exit(1)
