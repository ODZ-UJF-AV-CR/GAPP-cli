# GAPP-cli

This is command line app for uploading station position and telemetry to the [GAPP server](https://github.com/ODZ-UJF-AV-CR/GAPP)

## Installing

1. Install `uv` python package manager. [Install guide](https://docs.astral.sh/uv/getting-started/installation/).
2. Clone this repository
3. Install *GAPP*:
```shell
uv tool install .
```
4. Now you can execute `gapp`:
```shell
$ gapp -h
usage: gapp [-h] config_path

GAPP CLI Application

positional arguments:
  config_path  Path to TOML configuration file

optional arguments:
  -h, --help   show this help message and exit
```

## Running without `uv` (plain Python + pip)

If you do not want to install `uv`, you can run the app directly with `python3` and install dependencies via `pip3`:

1. Install dependencies:
```shell
pip3 install -r requirements.txt
```
2. Run from the repository root with `src` on `PYTHONPATH`:
```shell
PYTHONPATH=src python3 -m gapp.cli config.toml
```

## Running

You need toml config file:
```toml
[uploader]
enabled = true
station_callsign = ""
server_url = ""

[gpsd]
enabled = true
host = "127.0.0.1"
port = 2947
interval = 10

[mavlink]
callsign = ""
enabled = true
connection_string = "udpin:0.0.0.0:14550"
source_system = 1
source_component = 139
```

Start by:
```shell
$ gapp config.toml
```
