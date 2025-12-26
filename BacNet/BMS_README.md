# Building Management System (BMS) Simulator with BACnet Protocol

A comprehensive Python-based simulator for a Building Management System that includes sensor simulation and BACnet protocol support for client-server communication.

## Overview

This project provides:

1. **BMS Device Simulator** (`bms_simulator.py`) - Simulates a real building management system with 5 sensor parameters
2. **BACnet Server** (`bms_bacnet_server.py`) - Exposes sensor data via BACnet protocol for remote access
3. **BACnet Client** (`bms_bacnet_client.py`) - Python client to read data from BACnet servers
4. **Monitoring System** (`bms_monitor.py`) - Advanced monitoring with logging and statistics
5. **Demo Scripts** (`bms_demo.py`) - Interactive demonstrations of all features

## Features

### BMS Device (5 Sensor Parameters)

The simulator captures and provides realistic variations for:

1. **Temperature** (°C)
   - Range: 18-26°C
   - Realistic gradual changes with Gaussian distribution
   - Simulates HVAC effects

2. **Humidity** (%)
   - Range: 30-60%
   - Inverse correlation with temperature
   - Realistic daily variations

3. **Atmospheric Pressure** (hPa)
   - Range: 990-1030 hPa
   - Weather simulation
   - Small random variations

4. **CO2 Level** (ppm)
   - Range: 300-1000 ppm
   - Correlation with occupancy
   - Represents air quality

5. **Occupancy** (count)
   - Range: 0-100 people
   - Random entry/exit simulation
   - Affects CO2 levels

### BACnet Protocol Support

- **Server**: Exposes sensor data as BACnet AnalogInput objects
- **Client**: Reads remote sensor data via BACnet network communication
- **Standards**: Uses industry-standard BACnet/IP protocol
- **Threading**: Asynchronous server with background data updates

### Monitoring & Analytics

- Real-time data logging
- CSV and JSON export
- Statistical analysis (min/max/avg)
- Threshold-based alerts
- Multi-device support

## Installation

### Requirements

- Python 3.7+
- bacpypes library
- numpy (optional, for advanced features)

### Setup

1. **Install dependencies**:
   ```powershell
   C:\Python312\python.exe -m pip install bacpypes numpy
   ```

2. **Verify installation**:
   ```powershell
   C:\Python312\python.exe -c "import bacpypes; print('BACnet library installed')"
   ```

## Usage

### Quick Start - Standalone BMS

```python
from bms_simulator import BMSDevice
import time

# Create device
bms = BMSDevice(device_id="BMS-001", location="Building A - Office")

# Start simulation
bms.start_simulation(update_interval=1.0)

# Read sensor data
for i in range(5):
    data = bms.get_sensor_data()
    print(f"Temperature: {data['temperature']:.2f}°C")
    time.sleep(1)

bms.stop_simulation()
```

### BMS with BACnet Server

```python
from bms_simulator import BMSDevice
from bms_bacnet_server import BMSBACnetServer
import time

# Create and start BMS device
bms = BMSDevice(device_id="BMS-001", location="Building A")
bms.start_simulation(update_interval=1.0)

# Create and start BACnet server
server = BMSBACnetServer(
    bms_device=bms,
    device_id=12345,
    device_name="BMS-Server-01",
    local_address="192.168.1.100/24:47808"
)
server.initialize()
server.start()

# Server runs in background
time.sleep(30)

server.stop()
bms.stop_simulation()
```

### BACnet Client

```python
from bms_bacnet_client import BMSBACnetClient
import time

# Create client
client = BMSBACnetClient(
    local_address="192.168.1.101/24:47809",
    device_name="BMS-Client-01"
)

# Initialize and register remote device
client.initialize()
client.register_remote_device(
    device_id=12345,
    address="192.168.1.100:47808",
    name="BMS-Server-01"
)

# Read sensor data
temperature = client.read_property(
    device_id=12345,
    obj_type='analogInput',
    obj_instance=0,
    property_name='presentValue'
)

print(f"Temperature: {temperature}°C")

client.close()
```

### Monitoring System

```python
from bms_simulator import BMSDevice
from bms_monitor import BMSMonitor

# Create and start device
device = BMSDevice(device_id="OFFICE-A", location="Building A")
device.start_simulation(update_interval=0.5)

# Create monitor
monitor = BMSMonitor(output_dir="./bms_logs")
monitor.add_device(device)

# Run monitoring for 60 seconds
monitor.start_monitoring(interval=5.0, duration=60.0)

# Save and report
monitor.save_csv()
monitor.save_json()
monitor.print_report()

device.stop_simulation()
```

### Interactive Demo

Run the interactive demonstration:

```powershell
C:\Python312\python.exe bms_demo.py
```

This provides a menu-driven interface to:
- View BMS device operation
- Test BACnet server functionality
- Control sensors manually
- Monitor multiple devices

## API Reference

### BMSDevice

**Initialization**:
```python
device = BMSDevice(device_id: str, location: str)
```

**Methods**:
- `start_simulation(update_interval: float = 1.0)` - Start sensor simulation
- `stop_simulation()` - Stop simulation
- `get_sensor_data()` -> Dict - Get all sensor readings
- `get_sensor_value(sensor_name: str)` -> float - Get single sensor value
- `get_sensor_metadata(sensor_name: str)` -> Dict - Get sensor specs
- `set_sensor_value(sensor_name: str, value: float)` - Manually set value
- `get_device_info()` -> Dict - Get device metadata

### BMSBACnetServer

**Initialization**:
```python
server = BMSBACnetServer(
    bms_device: BMSDevice,
    device_id: int = 12345,
    device_name: str = "BMS-Device",
    local_address: str = "192.168.1.100/24:47808"
)
```

**Methods**:
- `initialize()` -> bool - Initialize BACnet application
- `start()` - Start BACnet server
- `stop()` - Stop server
- `get_sensor_value(sensor_name: str)` -> float - Get sensor via BACnet
- `get_device_info()` -> Dict - Get server info

### BMSBACnetClient

**Initialization**:
```python
client = BMSBACnetClient(
    local_address: str = "192.168.1.101/24:47809",
    device_name: str = "BMS-Client"
)
```

**Methods**:
- `initialize()` -> bool - Initialize client
- `register_remote_device(device_id, address, name)` - Register server
- `read_property(device_id, obj_type, obj_instance, property_name)` - Read remote data
- `read_sensor_data(device_id, sensor_names)` -> Dict - Read all sensors
- `discover_devices()` -> List - Discover network devices
- `close()` - Close client connection

### BMSMonitor

**Initialization**:
```python
monitor = BMSMonitor(output_dir: str = "./bms_logs")
```

**Methods**:
- `add_device(device: BMSDevice)` - Register device
- `start_monitoring(interval: float = 5.0, duration: Optional[float] = None)` - Start monitoring
- `save_csv(filename: Optional[str] = None)` - Export to CSV
- `save_json(filename: Optional[str] = None)` - Export to JSON
- `get_statistics(device_id: Optional[str] = None)` -> Dict - Calculate stats
- `print_report()` - Print summary report

## Network Configuration

### For Local Network Testing

When using on a local network, configure IP addresses appropriately:

**Server**:
```python
local_address="192.168.1.100/24:47808"  # Your server IP
```

**Client**:
```python
local_address="192.168.1.101/24:47809"  # Your client IP
register_remote_device(
    device_id=12345,
    address="192.168.1.100:47808"  # Server IP
)
```

### For Same Machine Testing

If server and client are on the same machine:

```python
# Server
server = BMSBACnetServer(..., local_address="127.0.0.1/24:47808")

# Client
client = BMSBACnetClient(local_address="127.0.0.1/24:47809")
client.register_remote_device(12345, "127.0.0.1:47808", "Local-Server")
```

## File Structure

```
bms_simulator.py         - Core BMS device simulator
bms_bacnet_server.py     - BACnet protocol server
bms_bacnet_client.py     - BACnet protocol client
bms_monitor.py           - Monitoring and analytics system
bms_demo.py              - Interactive demonstration
README.md                - This file
bms_logs/                - Auto-created directory for logs
```

## Examples

### Example 1: Basic Sensor Monitoring

```python
from bms_simulator import BMSDevice
import time

bms = BMSDevice(device_id="DEMO-01", location="Demo Building")
bms.start_simulation()

for i in range(10):
    data = bms.get_sensor_data()
    print(f"{data['temperature']:.1f}°C, "
          f"{data['humidity']:.1f}%, "
          f"{data['co2_level']:.0f}ppm")
    time.sleep(1)

bms.stop_simulation()
```

### Example 2: Multi-Building Monitoring

```python
from bms_simulator import BMSDevice
from bms_monitor import BMSMonitor
import time

monitor = BMSMonitor()

for floor in range(1, 4):
    device = BMSDevice(
        device_id=f"FLOOR-{floor}",
        location=f"Building A - Floor {floor}"
    )
    device.start_simulation(update_interval=0.5)
    monitor.add_device(device)

# Monitor for 5 minutes
monitor.start_monitoring(interval=10.0, duration=300.0)

monitor.save_csv("multi_building_log.csv")
monitor.print_report()
```

### Example 3: Custom Threshold Monitoring

```python
from bms_simulator import BMSDevice
from bms_monitor import BMSMonitor

device = BMSDevice(device_id="OFFICE", location="Conference Room")
device.start_simulation(update_interval=1.0)

monitor = BMSMonitor()
monitor.add_device(device)

# Customize thresholds
monitor.thresholds['temperature']['max'] = 24  # Alert if > 24°C

monitor.start_monitoring(interval=2.0, duration=60.0)
monitor.print_report()

device.stop_simulation()
```

## Troubleshooting

### BACnet Connection Issues

1. **Address already in use**: Change the port number in `local_address`
   ```python
   local_address="192.168.1.100/24:47810"  # Use different port
   ```

2. **Network unreachable**: Verify network configuration
   ```powershell
   ping 192.168.1.100
   ```

3. **Device not discovered**: Ensure server is running and initialized
   ```python
   if server.initialize():
       server.start()
   ```

### Data Not Updating

Ensure simulation is running:
```python
if device.running:
    data = device.get_sensor_data()
else:
    device.start_simulation()
```

## Performance Notes

- Simulation uses threading for non-blocking operation
- Update interval minimum: 0.1 seconds (for high-frequency data)
- 5 sensor parameters per device = minimal CPU/memory overhead
- Suitable for many concurrent devices

## Future Enhancements

- [ ] Database integration (SQLite/PostgreSQL)
- [ ] Web dashboard (Flask/FastAPI)
- [ ] Real sensor hardware integration
- [ ] Advanced anomaly detection (ML)
- [ ] Multi-building aggregation
- [ ] Energy consumption simulation

## License

This project is provided as-is for educational and development purposes.

## Support

For issues, questions, or contributions, please refer to the inline code documentation and examples.

---

Created: 2025-12-24
Version: 1.0.0
