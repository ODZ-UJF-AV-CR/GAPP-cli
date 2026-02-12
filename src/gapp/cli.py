import multiprocessing
import sys
import time

from gapp.config import get_config
from gapp.gps import run_gps_logger
from gapp.telemetry import run_telemetry_uploader


def main():
    # Load configuration (merges defaults, config file, and CLI args)
    config = get_config()

    processes = []

    # Create a shared queue for telemetry data
    # We create it regardless, but only use it if telemetry is enabled
    telemetry_queue = multiprocessing.Queue()

    # 1. Start Telemetry Uploader if server_url is configured
    server_url = config.get("server_url")
    station_callsign = config.get("station_callsign", "")

    if server_url:
        print(f"Starting telemetry uploader to {server_url}")
        p_telemetry = multiprocessing.Process(
            target=run_telemetry_uploader,
            args=(server_url, telemetry_queue, station_callsign),
        )
        processes.append(p_telemetry)
        p_telemetry.start()
    else:
        print("Telemetry upload disabled (no server_url configured)")

    # 2. Start GPSD Module if enabled
    gpsd_config = config.get("gpsd", {})
    if gpsd_config.get("enabled"):
        host = gpsd_config.get("host", "127.0.0.1")
        port = gpsd_config.get("port", 2947)

        # Only pass the queue if telemetry is actually running (server_url is set)
        queue_for_gps = telemetry_queue if server_url else None

        print(
            f"Starting GPSD logger (Queue: {'Enabled' if queue_for_gps else 'Disabled'})"
        )
        p_gps = multiprocessing.Process(
            target=run_gps_logger, args=(host, port, queue_for_gps)
        )
        processes.append(p_gps)
        p_gps.start()

    # Future modules (e.g., mavlink) will be added here in a similar way
    # mavlink_config = config.get("mavlink", {})
    # if mavlink_config.get("enabled"):
    #     queue_for_mav = telemetry_queue if server_url else None
    #     p_mav = multiprocessing.Process(target=run_mavlink, args=(..., queue_for_mav))
    #     processes.append(p_mav)
    #     p_mav.start()

    if not processes:
        print("No modules enabled.")
        return

    try:
        # Wait for all processes to complete (or run indefinitely)
        for p in processes:
            p.join()
    except KeyboardInterrupt:
        print("\nStopping all modules...")

        # Signal telemetry uploader to stop gracefully
        if server_url:
            telemetry_queue.put(None)

        for p in processes:
            if p.is_alive():
                p.terminate()
        sys.exit(0)


if __name__ == "__main__":
    main()
