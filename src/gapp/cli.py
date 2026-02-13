import multiprocessing
import sys

from gapp.config import get_config
from gapp.gps import run_gps_logger
from gapp.mavlink import run_mavlink_logger
from gapp.uploader import run_telemetry_uploader


def main():
    config = get_config()

    uploader_config = config.get("uploader", {})
    mavlink_config = config.get("mavlink", {})
    gpsd_config = config.get("gpsd", {})

    uploader_enabled = uploader_config.get("enabled")
    server_url = uploader_config.get("server_url")
    station_callsign = uploader_config.get("station_callsign")
    mavlink_callsign = mavlink_config.get("callsign")

    processes = []
    telemetry_queue = multiprocessing.Queue()


    if uploader_enabled and server_url and station_callsign:
        p_telemetry = multiprocessing.Process(
            target=run_telemetry_uploader,
            args=(server_url, telemetry_queue, station_callsign, mavlink_callsign),
        )
        processes.append(p_telemetry)
        p_telemetry.start()
    else:
        print(
            "Telemetry upload disabled (no server_url, station_callsign configured or disabled in config)"
        )
        server_url = None

    # 2. Start GPSD Module if enabled
    if gpsd_config.get("enabled"):
        host = gpsd_config.get("host")
        port = gpsd_config.get("port")
        interval = gpsd_config.get("interval")

        p_gps = multiprocessing.Process(
            target=run_gps_logger, args=(host, port, interval, telemetry_queue)
        )
        processes.append(p_gps)
        p_gps.start()

    # 3. Start MAVLink Module if enabled
    if mavlink_config.get("enabled"):
        connection_string = mavlink_config.get("connection_string")
        source_system = mavlink_config.get("source_system")
        source_component = mavlink_config.get("source_component")

        queue_for_mav = telemetry_queue if server_url else None

        p_mav = multiprocessing.Process(
            target=run_mavlink_logger,
            args=(connection_string, source_system, source_component, queue_for_mav),
        )
        processes.append(p_mav)
        p_mav.start()

    if not processes:
        print("No modules enabled.")
        return

    try:
        for p in processes:
            p.join()
    except KeyboardInterrupt:
        print("\nStopping all modules...")

        if server_url:
            telemetry_queue.put(None)

        for p in processes:
            if p.is_alive():
                p.terminate()
        sys.exit(0)


if __name__ == "__main__":
    main()
