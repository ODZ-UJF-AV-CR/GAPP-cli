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

## Running

You need toml config file:
```toml
[uploader]
enabled = true
station_callsign = "test2"
server_url = "http://localhost:3000"

[gpsd]
enabled = true
```

Start by:
```shell
$ gapp config.toml
```
