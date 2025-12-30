"""
BACnet-based BMS Server (bacpypes) - Simplified version

This file provides a simplified BACnet server wrapper around the BMS device
that avoids bacpypes' IAmRequest encoding issues by using a custom application
initialization.

Notes:
- Requires `bacpypes` to be installed and Python 3.11 recommended
- Uses a minimal BACnet setup to avoid initialization errors

Usage:
    from bms_simulator import BMSDevice
    from bms_bacnet_server_bacnet import BACnetBMSServer

    device = BMSDevice("BACNET-DEV1", "Floor 1")
    device.start_simulation()
    server = BACnetBMSServer(device, address='0.0.0.0:47808', device_id=12345)
    server.start()

    # Keep running, or run client examples to read values

    server.stop()
    device.stop_simulation()

"""

import threading
import time
import logging
from typing import Dict, Any, Optional

log = logging.getLogger(__name__)

try:
    # bacpypes imports
    from bacpypes.local.device import LocalDeviceObject
    from bacpypes.app import BIPSimpleApplication
    from bacpypes.core import run, stop, deferred
    from bacpypes.object import AnalogValueObject
    from bacpypes.primitivedata import Real
    BACPYPES_AVAILABLE = True
except Exception as e:
    BACPYPES_AVAILABLE = False
    log.error(f"bacpypes not available: {e}")


class BACnetBMSServer:
    """BACnet server exposing BMS sensor values via bacpypes.

    This class is intentionally minimal: it maps each numeric sensor to an
    `AnalogValue` object and updates the object's `presentValue` from the
    provided `device.get_sensor_data()` results.
    
    Exposes 6 sensors as BACnet AnalogValue objects:
    1. Total Electricity Energy (kWh)
    2. Outdoor Air Temperature (°C)
    3. Outdoor Air Humidity (%)
    4. Wind Speed (m/s)
    5. Diffuse Solar Radiation (W/m²)
    6. Direct Solar Radiation (W/m²)

    The server runs bacpypes `run()` in a background thread so the main
    program can continue. If `bacpypes` is not installed an informative
    exception will be raised.
    """

    def __init__(self, device, address="0.0.0.0:47808", device_id=12345):
        if not BACPYPES_AVAILABLE:
            raise ImportError(
                "bacpypes is required for BACnet implementation. "
                "Install with: pip install bacpypes (use Python 3.11 recommended)"
            )
        self.device = device
        self.address = address
        self.device_id = int(device_id)
        self._app = None
        self._local_device = None
        self._update_thread = None
        self._core_thread = None
        self._running = threading.Event()

        # mapping sensor_name -> bacpypes object
        self.objects = {}

        # Load server configuration (optional file 'server.config')
        # This will populate port, debug level, vendor and model metadata
        self._load_config()

        # allow overriding address by constructor parameter; if address left
        # as the default and config provided a port, update the address
        if address == "0.0.0.0:47808" and getattr(self, 'port', None):
            self.address = f"0.0.0.0:{self.port}"
        else:
            self.address = address

        self._init_application()

    def _load_config(self, path: str = "server.config"):
        """Load simple key=value config for server.

        Supported keys (case-insensitive):
          Port, DebugLevel, VendorName, VendorIdentifier, ModelName

        Values are applied to instance attributes: `port`, `vendorName`,
        `vendorIdentifier`, `modelName`, and logging level is set from
        `DebugLevel` when provided.
        """
        try:
            cfg = {}
            with open(path, "r", encoding="utf-8") as f:
                for raw in f:
                    line = raw.strip()
                    if not line or line.startswith('#'):
                        continue
                    if '=' not in line:
                        continue
                    key, val = line.split('=', 1)
                    cfg[key.strip().lower()] = val.strip()

            if not cfg:
                return

            # Port
            if 'port' in cfg:
                try:
                    self.port = int(cfg['port'])
                except Exception:
                    log.warning(f"Invalid Port value in {path}: {cfg.get('port')}")

            # Debug level
            if 'debuglevel' in cfg:
                lvl = cfg['debuglevel'].upper()
                level = getattr(logging, lvl, None)
                if isinstance(level, int):
                    logging.getLogger().setLevel(level)
                    log.info(f"Logging level set to {lvl}")
                else:
                    # try numeric
                    try:
                        numeric = int(cfg['debuglevel'])
                        logging.getLogger().setLevel(numeric)
                    except Exception:
                        log.warning(f"Unknown DebugLevel in {path}: {cfg.get('debuglevel')}")

            # Vendor and model info
            if 'vendorname' in cfg:
                self.vendorName = cfg['vendorname']
            if 'vendoridentifier' in cfg:
                try:
                    self.vendorIdentifier = int(cfg['vendoridentifier'])
                except Exception:
                    log.warning(f"Invalid VendorIdentifier in {path}: {cfg.get('vendoridentifier')}")
            if 'modelname' in cfg:
                self.modelName = cfg['modelname']

            log.info(f"Loaded server config from {path}")
        except FileNotFoundError:
            # not required; continue with defaults
            return
        except Exception as e:
            log.exception(f"Error loading config {path}: {e}")

    def _init_application(self):
        # Create a LocalDeviceObject with ONLY required fields
        # The vendorIdentifier must be set - use a default vendor code
        try:
            # Create the LocalDeviceObject with vendorIdentifier and other
            # descriptive properties passed in the constructor. Some bacpypes
            # versions expect vendorIdentifier as a constructor parameter.
            self._local_device = LocalDeviceObject(
                objectName=f"BMSDevice-{self.device_id}",
                objectIdentifier=("device", self.device_id),
                maxApduLengthAccepted=1024,
                segmentationSupported="noSegmentation",
                vendorIdentifier=getattr(self, 'vendorIdentifier', 47),
                vendorName=getattr(self, 'vendorName', "BMS Simulator"),
                modelName=getattr(self, 'modelName', "BMS BACnet Server"),
                systemStatus="operational",
            )
        except Exception as e:
            log.error(f"Failed to create LocalDeviceObject: {e}")
            raise

        # Create application and attach objects
        try:
            self._app = BIPSimpleApplication(self._local_device, self.address)
        except Exception as e:
            log.error(f"Failed to create BIPSimpleApplication: {e}")
            raise

        # Sensor objects will be created in start() method BEFORE core starts
        log.info(f"BACnet application initialized on {self.address}")

    def _add_sensors_as_objects(self):
        """Create 6 BMS sensor objects as AnalogValue instances in the BACnet device.
        MUST be called before bacpypes core starts."""
        try:
            # Sensor definitions: (instance, name, unit)
            sensors = [
                (1, "Total_Electricity_Energy", "kilowattHours"),
                (2, "Outdoor_Air_Temperature", "degreesCelsius"),
                (3, "Outdoor_Air_Humidity", "percentRelativeHumidity"),
                (4, "Wind_Speed", "metersPerSecond"),
                (5, "Diffuse_Solar_Radiation", "wattsPerSquareMeter"),
                (6, "Direct_Solar_Radiation", "wattsPerSquareMeter"),
            ]
            
            for instance, name, unit in sensors:
                try:
                    log.debug(f"Creating AnalogValueObject: {name} (instance {instance})")
                    analog_obj = AnalogValueObject(
                        objectIdentifier=('analogValue', instance),
                        objectName=name,
                        presentValue=Real(0.0),
                        units=unit,
                        description=f"BMS {name} sensor"
                    )
                    self._app.add_object(analog_obj)
                    self.objects[name] = analog_obj
                    log.info(f"✓ Added {name} (analogValue.{instance}) to BACnet device")
                except Exception as e:
                    log.error(f"✗ Failed to add {name}: {e}")
                    import traceback
                    traceback.print_exc()
        except Exception as e:
            log.exception(f"Failed to add sensor objects: {e}")
            raise

    def _update_loop(self):
        """Continuously update sensor object presentValues from device simulator."""
        log.info("Sensor update loop started")
        while self._running.is_set():
            try:
                sensor_data = self.device.get_sensor_data()
                if sensor_data:
                    # Update stored sensor objects with latest values
                    sensor_map = {
                        'Total_Electricity_Energy': sensor_data.get('electricity_energy', 0.0),
                        'Outdoor_Air_Temperature': sensor_data.get('outdoor_temp', 0.0),
                        'Outdoor_Air_Humidity': sensor_data.get('outdoor_humidity', 0.0),
                        'Wind_Speed': sensor_data.get('wind_speed', 0.0),
                        'Diffuse_Solar_Radiation': sensor_data.get('diffuse_solar', 0.0),
                        'Direct_Solar_Radiation': sensor_data.get('direct_solar', 0.0),
                    }
                    
                    for name, value in sensor_map.items():
                        try:
                            if name in self.objects:
                                obj = self.objects[name]
                                obj.presentValue = Real(float(value))
                                log.debug(f"Updated {name} = {value}")
                        except Exception as e:
                            log.error(f"Error updating {name}: {e}")
                
                time.sleep(1.0)  # Update every second
            except Exception as e:
                log.exception("Error in sensor update loop: %s", e)

    def start(self):
        """Start the BACnet server and sensor update thread.
        Critical: Sensor objects are added BEFORE bacpypes core starts."""
        if self._running.is_set():
            log.warning("Server already running")
            return
        
        log.info(f"BACnet server starting on {self.address}")
        
        # CRITICAL: Add sensor objects to device BEFORE starting bacpypes core
        try:
            self._add_sensors_as_objects()
            log.info("Sensor objects successfully added to BACnet device")
        except Exception as e:
            log.exception(f"Failed to add sensor objects: {e}")
            return
        
        # Start bacpypes core in background thread
        def _run_core():
            try:
                # Suppress IAmRequest encoding warnings during run
                import logging as bl
                bacpypes_logger = bl.getLogger('bacpypes')
                old_level = bacpypes_logger.level
                bacpypes_logger.setLevel(bl.ERROR)  # Only show errors, not debug
                
                run()
            except Exception as e:
                log.exception("bacpypes core exited: %s", e)
            finally:
                try:
                    bacpypes_logger.setLevel(old_level)
                except:
                    pass

        self._core_thread = threading.Thread(target=_run_core, daemon=True)
        self._core_thread.start()

        # Start sensor update thread
        self._update_thread = threading.Thread(target=self._update_loop, daemon=True)
        self._update_thread.start()
        
        self._running.set()
        log.info("BACnet server started, waiting for client requests...")

    def stop(self):
        """Stop the server and bacpypes core."""
        self._running.clear()
        try:
            stop()
        except Exception:
            pass
        log.info("BACnet server stopping")


if __name__ == "__main__":
    """Run the BACnet server as a standalone process.
    
    This script starts:
    1. A BMSDevice simulator (generates sensor data)
    2. A BACnet server that exposes the sensor data over the network
    
    The server will run on 0.0.0.0:47808 and can be accessed by remote
    BACnet clients (like bms_bacnet_client_bacnet.py).
    
    Press Ctrl-C to stop the server.
    """
    import time
    from bms_simulator import BMSDevice
    
    # Create and start the device simulator
    device = BMSDevice("BACNET-SERVER", "Standalone Server")
    device.start_simulation()
    print(f"[*] Device simulator started: {device.device_id} at {device.location}")
    
    # Create and start the BACnet server
    server = BACnetBMSServer(device, address="0.0.0.0:47808", device_id=12345)
    server.start()
    print("[*] BACnet server started on 0.0.0.0:47808")
    print("[*] Waiting for client connections (press Ctrl-C to stop)...")
    
    try:
        # Keep the server running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[*] Shutting down...")
        server.stop()
        device.stop_simulation()
        print("[*] Server stopped")
