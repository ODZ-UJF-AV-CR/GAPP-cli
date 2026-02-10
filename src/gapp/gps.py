import sys
from gpsdclient.client import GPSDClient


def run_gps_logger(host: str, port: int) -> None:
    """
    Connects to GPSD and streams TPV data to stdout.
    """
    print(f"Connecting to GPSD at {host}:{port}...")

    try:
        with GPSDClient(host=host, port=port) as client:
            for result in client.dict_stream(convert_datetime=True):
                # Filter for TPV (Time Position Velocity) reports which contain lat/lon/time
                if result.get("class") == "TPV":
                    lat = result.get("lat", "N/A")
                    lon = result.get("lon", "N/A")
                    time_str = result.get("time", "N/A")
                    print(f"Time: {time_str}, Lat: {lat}, Lon: {lon}")
    except ConnectionRefusedError:
        print(f"Error: Could not connect to GPSD at {host}:{port}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nStopping GPSD logging.")
        sys.exit(0)
    except Exception as e:
        print(f"An error occurred: {e}", file=sys.stderr)
        sys.exit(1)
