# internet_connection_monitor

Python-based util for logging internet connection status for given WiFi network SSIDs.

Uses NetworkManager to connect between given SSIDs.

* Free software: MIT license


## Usage
```
$ internet_connection_monitor -h
Usage: internet_connection_monitor [OPTIONS] ssid

  Repeatedly check internet connection status (connected or disconnected)
  for given WiFi SSIDs. Output is writen as .csv to stdout.

Options:
  -s, --sample-interval MINUTES  Duration (in minutes) between connectivity
                                 checks. Default=15.

  --no-header                    Disable printing of csv header row
  -h, --help                     Show this message and exit.
```

## Example Output
In this example, logging status for two SSIDs, one of which is not running, once per minute.
Output is formatted as .csv:
```
$ internet_connection_monitor Stuff-Fibre_48_2G TimAndroidWiFi -s 1
timestamp,ssid,device_connected,ping_successful
1608465542.6271882,Stuff-Fibre_48_2G,1,1
1608465572.9254916,TimAndroidWiFi,0,0
1608465599.5163016,Stuff-Fibre_48_2G,1,1
1608465629.8236022,TimAndroidWiFi,0,0
1608465659.5199883,Stuff-Fibre_48_2G,1,1
1608465689.8186944,TimAndroidWiFi,0,0
```


## Credits

This package was created with [Cookiecutter](https://github.com/audreyr/cookiecutter) and the [audreyr/cookiecutter-pypackage](https://github.com/audreyr/cookiecutter-pypackage) project template.

