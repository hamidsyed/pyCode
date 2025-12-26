"""
Small demo that starts the BACnet server (bacpypes) and a client that reads
values from it. This file is a convenience for quickly validating an
end-to-end BACnet flow on a single host.

Note: Running this requires `bacpypes` installed and a compatible Python
version (recommended: 3.11). Use separate terminals if you prefer to run
server and client independently.

Usage:
    python bms_bacnet_demo_bacnet.py

"""

import threading
import time

try:
    from bms_simulator import BMSDevice
    from bms_bacnet_server_bacnet import BACnetBMSServer
    from bms_bacnet_client_bacnet import BACnetBMSClient
except Exception as e:
    print("Make sure all demo files and bms_simulator.py exist in the same folder: ", e)
    raise


def run_demo():
    device = BMSDevice('BACNET-DEV-DEMO', 'Demo Room')
    device.start_simulation()

    server = BACnetBMSServer(device, address='127.0.0.1:47808', device_id=2001)
    server.start(poll_interval=1.0)

    # Give server time to start
    time.sleep(1.0)

    client = BACnetBMSClient(local_device_id=999, local_address='0.0.0.0:47809')
    client.start()

    try:
        for i in range(5):
            try:
                val = client.read_analog('127.0.0.1:47808', 'analogValue', 1)
                print(f"Read temperature (analogValue,1): {val}")
            except Exception as e:
                print('Read failed:', e)
            time.sleep(1.0)
    finally:
        client.stop()
        server.stop()
        device.stop_simulation()


if __name__ == '__main__':
    run_demo()
