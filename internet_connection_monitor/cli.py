"""Console script for internet_connection_monitor."""

# network manager code is based on the example:
# https://github.com/seveas/python-networkmanager/blob/master/examples/activate_connection.py
import sys
import subprocess
import time
import click
import NetworkManager
import atexit


def ping(host: str) -> bool:
    """
    ping host once, return True if successful
    """
    rc = subprocess.run(["ping", "-c", "1", host],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL).returncode
    return rc == 0


def wait_for_connection(device: NetworkManager.Device) -> bool:
    """
    Wait for the device connection to become active
    Return true if connection was made, false on timeout
    """
    # wait up to 'connect_timeout' seconds to connect
    connect_timeout = 30
    poll_time = 1
    connected = False
    start_time = time.time()

    def elapsed_time():
        return time.time() - start_time

    while not connected and elapsed_time() < connect_timeout:
        connected = device.State == NetworkManager.NM_DEVICE_STATE_ACTIVATED
        time.sleep(poll_time)

    return connected


@click.command(context_settings=dict(help_option_names=['-h', '--help']))
@click.argument('selected_ssids', nargs=-1, metavar="ssid")
@click.option(
    '--sample-interval',
    '-s',
    default=15,
    metavar="MINUTES",
    type=float,
    help="Duration (in minutes) between connectivity checks. Default=15.")
@click.option('--no-header',
              is_flag=True,
              help="Disable printing of csv header row")
def main(selected_ssids, sample_interval, no_header, args=None):
    """
    Repeatedly check internet connection status (connected or disconnected) for given WiFi SSIDs.
    Output is writen as .csv to stdout.
    """

    wireless_connections = [
        c for c in NetworkManager.Settings.Connections
        if '802-11-wireless' in c.GetSettings().keys()
    ]

    known_ssids = [
        c.GetSettings()['802-11-wireless']['ssid']
        for c in wireless_connections
    ]

    # confirm selected ssids are available as network manager connections
    for ssid in selected_ssids:
        assert ssid in known_ssids, f"SSID '{ssid}' not found in network manager connections. Available SSIDs: {sorted(known_ssids)}"

    # get the network manager connection objects for the selected ssids
    connections = {
        ssid: connection
        for connection in wireless_connections for ssid in selected_ssids
        if connection.GetSettings()['802-11-wireless']['ssid'] == ssid
    }

    # get the wireless device
    wireless_devs = [
        d for d in NetworkManager.NetworkManager.GetDevices()
        if d.DeviceType == NetworkManager.NM_DEVICE_TYPE_WIFI
    ]
    assert len(wireless_devs) > 0, "No wifi device found. Aborting"
    wireless_dev = wireless_devs[0]

    # save the current active connection, to restore once this script exits
    initial_connection = wireless_dev.ActiveConnection.Connection

    def restore_initial_connection():
        NetworkManager.NetworkManager.ActivateConnection(
            initial_connection, wireless_dev, "/")

    atexit.register(restore_initial_connection)

    # write the csv header
    if not no_header:
        print("timestamp,ssid,device_connected,ping_successful", flush=True)

    # begin logging loop.
    next_log_time = time.time()
    while True:

        # wait for the next logging iteration
        restore_initial_connection(
        )  # leave initial connection active while waiting
        time.sleep(max(next_log_time - time.time(), 0))
        next_log_time += sample_interval * 60

        for ssid in selected_ssids:
            # activate the connection

            if wireless_dev.State == NetworkManager.NM_DEVICE_STATE_ACTIVATED:
                wireless_dev.Disconnect()

            NetworkManager.NetworkManager.ActivateConnection(
                connections[ssid], wireless_dev, "/")

            connected = wait_for_connection(wireless_dev)

            if connected:
                # now test internet (by pinging google)
                ping_successful = ping("www.google.com")
            else:
                ping_successful = False

            # write out result
            print(
                f"{time.time()},{ssid},{int(connected)},{int(ping_successful)}",
                flush=True)

    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
