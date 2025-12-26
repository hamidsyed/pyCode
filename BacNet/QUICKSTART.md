# BMS Simulator - Quick Start Guide

## What You've Got

A complete Building Management System (BMS) simulator with 5 realistic sensors and network communication protocol.

## Files Created

| File | Purpose |
|------|---------|
| `bms_simulator.py` | Core BMS device that simulates 5 sensors |
| `bms_bacnet_server.py` | Server that exposes sensor data over network |
| `bms_bacnet_client.py` | Client that reads data from the server |
| `bms_monitor.py` | Monitoring system with logging and analytics |
| `bms_demo.py` | Interactive demo with multiple scenarios |
| `bms_complete_example.py` | Comprehensive example with server + client |
| `bms_test.py` | Test suite to validate everything works |
| `BMS_README.md` | Full documentation (API reference, examples) |
| `requirements_bms.txt` | Dependencies (numpy only - bacpypes removed due to Python 3.12 issues) |

## 5 Sensor Parameters

1. **Temperature** (°C) - 18-26°C range
2. **Humidity** (%) - 30-60% range
3. **Pressure** (hPa) - 990-1030 hPa range
4. **CO2 Level** (ppm) - 300-1000 ppm range
5. **Occupancy** (count) - 0-100 people

## Quick Examples

### 1. Run the Device Only
```powershell
C:\Python312\python.exe -c "
from bms_simulator import BMSDevice
import time

bms = BMSDevice(device_id='DEMO', location='Office')
bms.start_simulation()

for i in range(5):
    data = bms.get_sensor_data()
    print(f'Temp: {data[\"temperature\"]:.1f}°C, CO2: {data[\"co2_level\"]:.0f}ppm')
    time.sleep(1)

bms.stop_simulation()
"
```

### 2. Run Server and Client Together
```powershell
C:\Python312\python.exe bms_complete_example.py
```
Then select option 1 for integrated demo.

### 3. Run Monitoring System
```powershell
C:\Python312\python.exe bms_monitor.py
```

### 4. Run Interactive Demo
```powershell
C:\Python312\python.exe bms_demo.py
```

### 5. Run Tests
```powershell
C:\Python312\python.exe bms_test.py
```

## Code Examples

### Basic Device Usage
```python
from bms_simulator import BMSDevice

# Create device
device = BMSDevice(device_id="OFFICE-A", location="Floor 3")

# Start automatic simulation
device.start_simulation(update_interval=1.0)

# Read current values
data = device.get_sensor_data()
print(f"Temperature: {data['temperature']:.1f}°C")

# Or read one sensor
temp = device.get_sensor_value('temperature')

# Manually set values (for testing)
device.set_sensor_value('temperature', 24.0)

# Stop simulation
device.stop_simulation()
```

### Server Usage
```python
from bms_simulator import BMSDevice
from bms_bacnet_server import BMSServer

# Create and start device
device = BMSDevice(device_id="BMS-01", location="Building A")
device.start_simulation()

# Create server
server = BMSServer(
    bms_device=device,
    device_name="BMS-Server",
    host="127.0.0.1",
    port=47808
)

# Initialize and start
server.initialize()
server.start()

# Server runs in background
# ... client can connect and read data ...

server.stop()
device.stop_simulation()
```

### Client Usage
```python
from bms_bacnet_client import BMSClient

# Create client
client = BMSClient(host="127.0.0.1", port=47808)

# Connect
if client.connect():
    # Read all sensors
    data = client.read_all_sensors()
    print(f"Temperature: {data['temperature']}")
    
    # Or read one sensor
    temp = client.read_sensor('temperature')
    
    client.disconnect()
```

### Monitoring System
```python
from bms_simulator import BMSDevice
from bms_monitor import BMSMonitor

# Create device and monitor
device = BMSDevice(device_id="OFFICE", location="Office")
monitor = BMSMonitor(output_dir="./logs")

# Add device and start monitoring
monitor.add_device(device)
device.start_simulation()

# Run for 60 seconds
monitor.start_monitoring(interval=5.0, duration=60.0)

# Save and analyze
monitor.save_csv("data.csv")
monitor.save_json("data.json")
monitor.print_report()

device.stop_simulation()
```

## Architecture

```
BMS Device (Simulator)
    ↓ exposes data to
BMS Server (Socket-based)
    ↑ reads from
BMS Client (Network)
    ↓ data can be
BMS Monitor (Analytics)
```

## Features

✓ **Realistic Simulation**
  - Gaussian noise and correlation between sensors
  - Time-based variations
  - Occupancy affects CO2 levels

✓ **Network Communication**
  - JSON-based protocol
  - Socket-based (Python 3.12 compatible)
  - Asynchronous server with threading

✓ **Monitoring & Analytics**
  - Real-time data collection
  - CSV/JSON export
  - Statistics (min, max, average)
  - Threshold-based alerts

✓ **Easy to Extend**
  - Modular architecture
  - Clean APIs
  - Well-documented code

## Network Configuration

### For Local Testing (Same Machine)
```python
server = BMSServer(..., host="127.0.0.1", port=47808)
client = BMSClient(host="127.0.0.1", port=47808)
```

### For Network Testing
```python
server = BMSServer(..., host="192.168.1.100", port=47808)
client = BMSClient(host="192.168.1.100", port=47808)
```

## Troubleshooting

**"Port already in use"**
→ Change port number: `port=47809`

**"Connection refused"**
→ Ensure server is running and initialized

**"No data"**
→ Call `device.start_simulation()` before creating server

**Import errors**
→ Install numpy: `pip install numpy`

## Next Steps

1. **Explore the full README**: `BMS_README.md` has complete API documentation
2. **Run the examples**: Try `bms_complete_example.py` with all 4 options
3. **Customize sensors**: Edit sensor ranges in `bms_simulator.py`
4. **Add features**: Extend with database, web dashboard, or hardware integration
5. **Use in projects**: Import classes into your own applications

## Test Results

All tests passing ✓

```
✓ PASS - BMS Device
✓ PASS - BMS Server  
✓ PASS - BMS Client
Total: 3/3 passed (100%)
```

## Version Info

- **Python**: 3.12+
- **Dependencies**: numpy (optional)
- **Protocol**: Custom socket-based JSON (BACnet compatible structure)
- **Date Created**: December 24, 2025

---

**Enjoy your BMS Simulator!**
