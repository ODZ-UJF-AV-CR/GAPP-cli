import multiprocessing
import sys

from gapp.config import get_config
from gapp.gps import run_gps_logger
from gapp.uploader import run_telemetry_uploader


def main():
    config = get_config()

    processes = []

    telemetry_queue = multiprocessing.Queue()

    uploader_config = config.get("uploader", {})
    uploader_enabled = uploader_config.get("enabled")
    server_url = uploader_config.get("server_url")
    station_callsign = uploader_config.get("station_callsign")

    if uploader_enabled and server_url and station_callsign:
        print(f"Starting telemetry uploader to {server_url}")
        p_telemetry = multiprocessing.Process(
            target=run_telemetry_uploader,
            args=(server_url, telemetry_queue, station_callsign),
        )
        processes.append(p_telemetry)
        p_telemetry.start()
    else:
        print("Telemetry upload disabled (no server_url, station_callsign configured or disabled in config)")
        server_url = None

    # 2. Start GPSD Module if enabled
    gpsd_config = config.get("gpsd", {})
    if gpsd_config.get("enabled"):
        host = gpsd_config.get("host")
        port = gpsd_config.get("port")
        interval = gpsd_config.get("interval")

        p_gps = multiprocessing.Process(
            target=run_gps_logger, args=(host, port, interval, telemetry_queue)
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
