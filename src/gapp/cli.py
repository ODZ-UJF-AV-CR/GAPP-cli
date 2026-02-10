import multiprocessing
import sys
import time

from gapp.config import get_config
from gapp.gps import run_gps_logger


def main():
    # Load configuration (merges defaults, config file, and CLI args)
    config = get_config()

    processes = []

    # Application Logic
    # Dispatch to appropriate modules based on configuration
    # Note: Config structure is now nested: config["gpsd"]["enabled"], etc.

    gpsd_config = config.get("gpsd", {})
    if gpsd_config.get("enabled"):
        host = gpsd_config.get("host", "127.0.0.1")
        port = gpsd_config.get("port", 2947)

        # Start GPSD logger in a separate process
        p = multiprocessing.Process(target=run_gps_logger, args=(host, port))
        processes.append(p)
        p.start()

    # Future modules (e.g., mavlink) will be added here in a similar way
    # mavlink_config = config.get("mavlink", {})
    # if mavlink_config.get("enabled"):
    #     ...

    if not processes:
        # If no modules are enabled, just exit (or maybe print a message)
        print("No modules enabled.")
        return

    try:
        # Wait for all processes to complete (or run indefinitely)
        for p in processes:
            p.join()
    except KeyboardInterrupt:
        print("\nStopping all modules...")
        for p in processes:
            if p.is_alive():
                p.terminate()
        sys.exit(0)


if __name__ == "__main__":
    main()
