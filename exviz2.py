from pyezviz import EzvizClient

# Create an instance of EzvizClient
client = EzvizClient('your_username', 'your_password')

# Get a list of all devices
devices = client.get_device_list()

# Print the device list
for device in devices:
    print(f"Device name: {device['deviceName']}, device ID: {device['deviceSerial']}")

