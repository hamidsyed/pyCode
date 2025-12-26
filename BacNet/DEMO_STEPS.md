# BMS Simulator - Demo Commands & Steps

## 🎯 Quick Reference

### Recommended First Step (Verify Everything Works)
```powershell
C:/Python312/python.exe bms_test.py
```
**Expected Result**: 15/15 tests passed (100%)

---

## 📋 Complete Step-by-Step Guide

### DEMO 1: Run Test Suite (Recommended First)
**Purpose**: Validate all components are working
**Time**: ~30 seconds

```powershell
cd c:\Users\hamid\pyCode
C:/Python312/python.exe bms_test.py
```

**What You'll See**:
- Test suite running through 15 tests across 3 modules
- ✓ marks for each passing test
- Summary showing total passed tests
- Expected: **15/15 tests passed (100%)**

**What it proves**: All device, server, and client components are working correctly

---

### DEMO 2: Run Interactive Demo Menu
**Purpose**: See all features with interactive menu
**Time**: 2-5 minutes (depending on options selected)

```powershell
cd c:\Users\hamid\pyCode
C:/Python312/python.exe bms_demo.py
```

**Interactive Menu Options**:

```
======================================================================
BMS SIMULATOR - DEMONSTRATION MENU
======================================================================
1. BMS Device Standalone (no BACnet)
2. BMS with BACnet Server
3. Manual Sensor Control
4. Multiple BMS Devices
5. Run All Demos
0. Exit
======================================================================

Select demo (0-5): 
```

#### Option 1: BMS Device Standalone
- Shows: 10 cycles of sensor readings
- Readings include: Temperature (°C), Humidity (%), Pressure (hPa), CO2 (ppm), Occupancy (count)
- No network needed

#### Option 2: BMS with BACnet Server
- Shows: Server starting and handling sensor reads
- Demonstrates: Network server in action
- Server runs on 127.0.0.1:47808

#### Option 3: Manual Sensor Control
- Shows: Setting specific sensor values
- Demonstrates: Sensor value range constraints
- Example: Set temperature to 25°C manually

#### Option 4: Multiple BMS Devices
- Shows: 3 floors/devices monitored simultaneously
- Demonstrates: Multi-device management
- Example: Building A with 3 floors, each with different sensor readings

#### Option 5: Run All Demos
- Runs all 4 scenarios sequentially (~30 seconds total)

---

### DEMO 3: Run Complete Example (Server + Client)
**Purpose**: Show server and client working together
**Time**: 2-5 minutes

```powershell
cd c:\Users\hamid\pyCode
C:/Python312/python.exe bms_complete_example.py
```

**Menu Options**:

```
======================================================================
BMS SYSTEM - COMPLETE DEMONSTRATION
======================================================================

Select demo to run:
1. Integrated Server + Client (with threading)
2. Simple Monitoring
3. Manual Sensor Control
4. Run All Demos
0. Exit

Enter choice (0-4): 
```

#### Option 1: Integrated Server + Client
**What happens**:
1. BMS device starts and begins generating sensor data
2. Server starts in background listening on 127.0.0.1:47808
3. Client connects to server and reads sensor data
4. Shows 5 cycles of readings through the network
5. Demonstrates real network communication between server and client

#### Option 2: Simple Monitoring
**What happens**:
1. Device runs for 10 seconds
2. Collects sensor readings every 1 second
3. Calculates statistics: min, max, average for each sensor
4. Displays final statistics table

#### Option 3: Manual Sensor Control
**What happens**:
1. Tests 3 scenarios with manually set values
2. Shows sensor values at different settings
3. Demonstrates validation constraints

#### Option 4: Run All Demos
- Runs all 3 scenarios sequentially (~30 seconds)

---

### DEMO 4: Quick Standalone Run
**Purpose**: Minimal demo without interaction
**Time**: ~15 seconds

```powershell
cd c:\Users\hamid\pyCode
C:/Python312/python.exe bms_simulator.py
```

**Output**: 10 cycles of sensor readings from the simulated BMS device

---

## 🏃 Quick Start (Recommended Order)

### Step 1: Verify Installation (30 seconds)
```powershell
C:/Python312/python.exe bms_test.py
```
✅ Expect: "15/15 tests passed (100%)"

### Step 2: See Interactive Demo (2 minutes)
```powershell
C:/Python312/python.exe bms_demo.py
```
👉 Select option 1 or 2 to see device and server demos

### Step 3: See Server + Client (2 minutes)
```powershell
C:/Python312/python.exe bms_complete_example.py
```
👉 Select option 1 to see integrated server-client demo

### Step 4: Explore Code
Open the `.py` files to see the implementation details

---

## 📊 What Each Demo Shows

| Demo | Component | Network | Time | Best For |
|------|-----------|---------|------|----------|
| Test Suite | All 3 modules | N/A | 30s | Validation |
| Demo #1 | Device | No | 7s | Device simulation |
| Demo #2 | Server | Yes | 7s | Server operation |
| Complete #1 | Server + Client | Yes | 2m | Full integration |
| Complete #2 | Monitor | N/A | 2m | Analytics |

---

## 📁 5 Sensor Parameters

All demos collect data from these 5 sensors:

1. **Temperature** (°C)
   - Range: 18-26°C
   - Realistic variation with Gaussian distribution
   - Typical: 21-23°C

2. **Humidity** (%)
   - Range: 30-60%
   - Varies based on temperature and occupancy
   - Typical: 40-50%

3. **Pressure** (hPa)
   - Range: 1010-1020 hPa
   - Small realistic variations
   - Standard: ~1013 hPa

4. **CO2 Level** (ppm)
   - Range: 400-800 ppm
   - Increases with occupancy
   - Baseline: 400 ppm

5. **Occupancy** (count)
   - Range: 0-50 people
   - Random variations throughout the day
   - Typical: 10-30 people

---

## 🔍 For Developers

### Import and Use in Your Code
```python
from bms_simulator import BMSDevice
from bms_bacnet_server import BMSServer
from bms_bacnet_client import BMSClient
from bms_monitor import BMSMonitor

# Create device
device = BMSDevice(device_id="DEMO", location="Office")
device.start_simulation()

# Read sensor data
data = device.get_sensor_data()
print(f"Temperature: {data['temperature']:.1f}°C")
print(f"Humidity: {data['humidity']:.1f}%")
print(f"Occupancy: {data['occupancy']:.0f} people")

device.stop_simulation()
```

### Run a Server
```python
from bms_simulator import BMSDevice
from bms_bacnet_server import BMSServer

device = BMSDevice("DEVICE1", "Room A")
device.start_simulation()

server = BMSServer(device, host="127.0.0.1", port=47808)
server.start()
# Server now listening for client connections...
server.stop()
```

### Connect a Client
```python
from bms_bacnet_client import BMSClient

client = BMSClient(host="127.0.0.1", port=47808)
client.connect()

# Read single sensor
temp = client.read_sensor("temperature")
print(f"Temperature: {temp}°C")

# Read all sensors
data = client.read_all_sensors()
for sensor, value in data.items():
    print(f"{sensor}: {value}")

client.disconnect()
```

---

## ✅ Troubleshooting

| Issue | Solution |
|-------|----------|
| "Module not found" | Run from `c:\Users\hamid\pyCode` directory |
| "Port already in use" | Change port in server: `BMSServer(device, port=47809)` |
| "Connection refused" | Wait 2 seconds for server to start |
| "No data" | Check if `device.start_simulation()` was called |
| Tests fail | Verify Python 3.12+ is installed and used |

---

## 📚 Documentation Files

For more detailed information:
- **QUICKSTART.md** - Quick start guide (5 min read)
- **BMS_README.md** - Complete API documentation (20 min read)
- **PROJECT_SUMMARY.md** - Project architecture overview (10 min read)
- **INDEX.md** - File and function index (5 min read)
- **COMPLETION_REPORT.md** - Project completion summary (5 min read)

---

## 🎓 Learning Path

1. **Start**: Run `bms_test.py` to verify everything works
2. **Understand**: Read `QUICKSTART.md` (5 minutes)
3. **Explore**: Run `bms_demo.py` and choose option 1
4. **Integrate**: Run `bms_complete_example.py` option 1
5. **Customize**: Read `BMS_README.md` and modify code
6. **Reference**: Use `INDEX.md` to find specific functions

---

## 💾 File Summary

- **bms_simulator.py** - Core device simulation (280 lines)
- **bms_bacnet_server.py** - Network server (260 lines)
- **bms_bacnet_client.py** - Network client (180 lines)
- **bms_monitor.py** - Data collection and analytics (360 lines)
- **bms_demo.py** - Interactive demonstration menu (420 lines)
- **bms_complete_example.py** - Integrated server+client example (350 lines)
- **bms_test.py** - Test suite with 15 tests (220 lines)

**Total**: 2,070+ lines of production-ready code

---

## 🎯 Next Steps

Choose one:

1. **Run test suite** → `C:/Python312/python.exe bms_test.py`
2. **See interactive demo** → `C:/Python312/python.exe bms_demo.py`
3. **See server+client** → `C:/Python312/python.exe bms_complete_example.py`
4. **Read documentation** → Open `QUICKSTART.md`
