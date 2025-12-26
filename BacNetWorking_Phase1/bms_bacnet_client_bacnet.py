"""
BACnet-based BMS Client (bacpypes)

This client demonstrates how to read `presentValue` from AnalogValue objects
exposed by the `bms_bacnet_server_bacnet.py` server using `bacpypes`.

Note: bacpypes networking API can be low-level. The example below uses a
simple synchronous request/response pattern. For robust production use you
should follow bacpypes examples and handle retries/timeouts properly.

Usage:
    from bms_bacnet_client_bacnet import BACnetBMSClient
    client = BACnetBMSClient(local_device_id=999, local_address='0.0.0.0:47809')
    client.start()
    val = client.read_analog('127.0.0.1:47808', 'analogValue', 1)
    print(val)
    client.stop()

"""

import logging
import time
import threading
import datetime
import sqlite3
from typing import Optional, Dict, Any

log = logging.getLogger(__name__)

try:
    from bacpypes.local.device import LocalDeviceObject
    from bacpypes.app import BIPSimpleApplication
    from bacpypes.core import run, stop, deferred
    from bacpypes.pdu import Address
    from bacpypes.apdu import ReadPropertyRequest
    from bacpypes.iocb import IOCB
    from bacpypes.object import get_object_class
    BACPYPES_AVAILABLE = True
except Exception:
    BACPYPES_AVAILABLE = False

class DBHandler:
    """Simple database handler. Supports SQLite by default. Optionally
    supports Postgres if `psycopg2` is available and `db_type` is set to
    "postgres" in the config.

    Config example:
      {
          "db_type": "sqlite",              # or 'postgres'
          "database": "bms_bacnet.db",     # sqlite file or database name
          "table": "bms_readings",
          # postgres-only fields:
          "host": "localhost",
          "port": 5432,
          "user": "user",
          "password": "pass",
      }
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config.copy()
        self.db_type = (self.config.get("db_type") or "sqlite").lower()
        self.table = self.config.get("table", "bms_readings")
        self.conn = None
        self._connect()

    def _connect(self):
        if self.db_type == "sqlite":
            self.conn = sqlite3.connect(self.config.get("database", "bms_bacnet.db"), check_same_thread=False)
        elif self.db_type == "postgres":
            try:
                import psycopg2
            except Exception:
                raise ImportError("psycopg2 is required for Postgres support")
            self.conn = psycopg2.connect(
                dbname=self.config.get("database"),
                user=self.config.get("user"),
                password=self.config.get("password"),
                host=self.config.get("host", "localhost"),
                port=self.config.get("port", 5432),
            )
        else:
            raise ValueError(f"Unsupported db_type: {self.db_type}")

    def init_table(self):
        cur = self.conn.cursor()
        if self.db_type == "sqlite":
            cur.execute(f"""
            CREATE TABLE IF NOT EXISTS {self.table} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                device TEXT,
                object_type TEXT,
                instance INTEGER,
                sensor_name TEXT,
                value TEXT
            )
            """)
            self.conn.commit()
        else:
            # Postgres: use a simple create statement
            cur.execute(f"""
            CREATE TABLE IF NOT EXISTS {self.table} (
                id SERIAL PRIMARY KEY,
                timestamp TIMESTAMP,
                device TEXT,
                object_type TEXT,
                instance INTEGER,
                sensor_name TEXT,
                value TEXT
            )
            """)
            self.conn.commit()

    def insert_sensor_reading(self, record: Dict[str, Any]):
        cur = self.conn.cursor()
        if self.db_type == "sqlite":
            cur.execute(
                f"INSERT INTO {self.table} (timestamp, device, object_type, instance, sensor_name, value) VALUES (?, ?, ?, ?, ?, ?)",
                (
                    record.get("timestamp"),
                    record.get("device"),
                    record.get("object_type"),
                    record.get("instance"),
                    record.get("sensor_name"),
                    str(record.get("value")),
                ),
            )
        else:
            cur.execute(
                f"INSERT INTO {self.table} (timestamp, device, object_type, instance, sensor_name, value) VALUES (%s, %s, %s, %s, %s, %s)",
                (
                    record.get("timestamp"),
                    record.get("device"),
                    record.get("object_type"),
                    record.get("instance"),
                    record.get("sensor_name"),
                    str(record.get("value")),
                ),
            )
        self.conn.commit()

    def close(self):
        try:
            if self.conn:
                self.conn.close()
        except Exception:
            pass



class BACnetBMSClient:
    """Minimal BACnet client wrapper using bacpypes to read object properties.

    This client creates a local application and provides a `read_analog`
    convenience method that reads the `presentValue` of an analogValue
    instance on a remote device/address.
    """

    def __init__(self, local_device_id=999, local_address="0.0.0.0:47809", db_config: Optional[Dict[str, Any]] = None):
        if not BACPYPES_AVAILABLE:
            raise ImportError(
                "bacpypes is required for BACnet implementation. "
                "Install with: pip install bacpypes (use Python 3.11 recommended)"
            )
        # Ensure bacpypes LocalDeviceObject class has a vendorIdentifier
        # set for auto-registration compatibility across versions.
        try:
            LocalDeviceObject.vendorIdentifier = getattr(LocalDeviceObject, 'vendorIdentifier', 47)
        except Exception:
            # best-effort: ignore if not supported
            pass

        # Use tuple ("device", instance) as objectIdentifier
        self.local_device = LocalDeviceObject(
            objectName=f"BMSClient-{local_device_id}", 
            objectIdentifier=("device", int(local_device_id)),
            vendorIdentifier=47,
            vendorName="BMS Simulator")
        
        self.app = BIPSimpleApplication(self.local_device, local_address)
        self._core_thread = None
        # optional database handler
        self.db = None
        if db_config is None:
            # default: sqlite file in working directory
            db_config = {
                "db_type": "sqlite",
                "database": "bms_bacnet.db",
                "table": "bms_readings",
            }
        try:
            self.db = DBHandler(db_config)
            self.db.init_table()
        except Exception as e:
            log.warning("Database handler initialization failed: %s", e)

    def _run_core(self):
        try:
            run()
        except Exception as e:
            log.exception("bacpypes core exited: %s", e)

    def start(self):
        # run bacpypes core in background
        self._core_thread = threading.Thread(target=self._run_core, daemon=True)
        self._core_thread.start()
        # allow core to start
        time.sleep(0.2)

    def stop(self):
        try:
            stop()
        except Exception:
            pass

    def _convert_bacpypes_value(self, val):
        """Convert bacpypes type objects to primitive Python values.
        
        Handles Real, Integer, Any, and other bacpypes types.
        """
        import struct
        log.debug(f"Converting bacpypes value type={type(val).__name__}, repr={repr(val)}")

        # Strategy 1: Direct float conversion for Real, Integer, etc.
        try:
            result = float(val)
            log.debug(f"Direct float() conversion succeeded: {result}")
            return result
        except (TypeError, ValueError) as e:
            log.debug(f"Direct float() conversion failed: {e}")

        # Strategy 2: For Any type, extract from tagList (Tag objects)
        if type(val).__name__ == 'Any':
            log.debug("Handling Any type object")
            try:
                if hasattr(val, 'tagList'):
                    tag_list = val.tagList
                    log.debug(f"Any.tagList = {tag_list}")

                    for tag in tag_list:
                        log.debug(f"Tag from tagList: {tag}, type={type(tag).__name__}")

                        # 1) try tag.cast_out() if available (bacpypes Tag may expose cast_out)
                        if hasattr(tag, 'cast_out'):
                            try:
                                casted = tag.cast_out()
                                if casted is not None:
                                    try:
                                        return float(casted)
                                    except Exception:
                                        log.debug(f"cast_out returned non-numeric: {casted}")
                            except Exception as e:
                                log.debug(f"tag.cast_out() failed: {e}")

                        # 2) try tag.value (often contains the decoded primitive)
                        if hasattr(tag, 'value'):
                            try:
                                tag_value = tag.value
                                log.debug(f"Tag.value = {tag_value}, type={type(tag_value).__name__}")
                                return float(tag_value)
                            except Exception as e:
                                log.debug(f"Tag.value conversion failed: {e}")

                        # 3) try raw tagData bytes (bytearray/bytes) -> IEEE-754
                        if hasattr(tag, 'tagData'):
                            try:
                                td = tag.tagData
                                if isinstance(td, bytearray):
                                    td = bytes(td)
                                if isinstance(td, (bytes, bytearray)):
                                    b = bytes(td)
                                    try:
                                        if len(b) == 4:
                                            res = struct.unpack('>f', b)[0]
                                            log.debug(f"Decoded 4-byte float from Tag.tagData: {res}")
                                            return float(res)
                                        elif len(b) == 8:
                                            res = struct.unpack('>d', b)[0]
                                            log.debug(f"Decoded 8-byte double from Tag.tagData: {res}")
                                            return float(res)
                                    except struct.error as se:
                                        log.debug(f"struct.unpack failed on tagData: {se}")
                                else:
                                    # fallback: try converting tagData directly
                                    try:
                                        return float(td)
                                    except Exception:
                                        log.debug(f"Tag.tagData not numeric: {td}")
                            except Exception as e:
                                log.debug(f"Tag.tagData conversion failed: {e}")

                # If tagList yielded nothing, try dict_contents as fallback
                if hasattr(val, 'dict_contents'):
                    try:
                        contents = val.dict_contents()
                        log.debug(f"Any.dict_contents() = {contents}")
                        if contents:
                            for key, value in contents.items():
                                try:
                                    return float(value)
                                except Exception:
                                    continue
                    except Exception as e:
                        log.debug(f"Any.dict_contents() failed: {e}")
            except Exception as e:
                log.debug(f"Any handling failed: {e}")

        # Strategy 3: Check for _value attribute
        if hasattr(val, '_value'):
            try:
                inner = val._value
                log.debug(f"Extracted _value: {inner}")
                return float(inner)
            except Exception as e:
                log.debug(f"_value extraction failed: {e}")

        # Strategy 4: Check for value attribute
        if hasattr(val, 'value') and not callable(val.value):
            try:
                result = float(val.value)
                log.debug(f"Converted value attribute to float: {result}")
                return result
            except Exception as e:
                log.debug(f"value attribute extraction failed: {e}")

        log.warning(f"Could not convert bacpypes value type={type(val).__name__}, repr={repr(val)}")
        return None

    def read_analog(self, target_address, object_type, instance, timeout=2.0):
        """Read presentValue from a remote analogValue instance.

        target_address: 'host:port' string, e.g. '127.0.0.1:47808'
        object_type: typically 'analogValue'
        instance: integer instance number
        Returns the numeric value or None if read fails
        """
        addr = Address(target_address)
        # Build ReadPropertyRequest
        request = ReadPropertyRequest(
            objectIdentifier=(object_type, int(instance)),
            propertyIdentifier='presentValue',
        )
        request.pduDestination = addr

        # send and wait for response via IOCB
        try:
            iocb = IOCB(request)
            self.app.request_io(iocb)
            iocb.wait(timeout)
            
            if iocb.ioError:
                log.error(f"BACnet read error: {iocb.ioError}")
                return None
                
            if iocb.ioResponse is None:
                log.warning("No BACnet response received for read")
                return None
                
            # read value from response
            resp = iocb.ioResponse
            
            # Extract presentValue from response
            pv = None
            try:
                if hasattr(resp, 'propertyValue'):
                    pv = resp.propertyValue
                    log.debug(f"Got propertyValue: {pv}, type={type(pv).__name__}")
            except Exception as e:
                log.debug(f"Error accessing propertyValue: {e}")
                return None
            
            if pv is None:
                log.warning(f"Could not extract presentValue from response")
                return None
            
            # Convert bacpypes types to primitive Python values
            value_to_store = self._convert_bacpypes_value(pv)
            
            if value_to_store is None:
                log.error(f"Failed to convert response value")
                return None
            
            # write to database if available
            try:
                if self.db is not None:
                    sensor_name = f"{object_type}.{instance}"
                    self.db.insert_sensor_reading({
                        "timestamp": datetime.datetime.utcnow().isoformat(),
                        "device": str(target_address),
                        "object_type": object_type,
                        "instance": int(instance),
                        "sensor_name": sensor_name,
                        "value": value_to_store,
                    })
            except Exception:
                log.exception("Failed to insert sensor reading into DB")

            log.debug(f"Read {object_type}.{instance} = {value_to_store}")
            return value_to_store
            
        except Exception as e:
            log.error(f"BACnet read failed: {e}")
            return None


if __name__ == "__main__":
    """Standalone client: poll all 5 BMS sensors and print to stdout.

    Runs indefinitely until interrupted (Ctrl-C). Reads all analogValue
    instances (1..5) from `127.0.0.1:47808` and prints a single-line sensor
    summary each second similar to the server output.
    """
    client = BACnetBMSClient(local_device_id=999, local_address='0.0.0.0:47809')

    def read_all_sensors(client_obj, target='127.0.0.1:47808'):
        """Read all configured analogValue sensors and return a dict.

        Returns dict with keys: Temperature, Humidity, Pressure, CO2_Level, Occupancy
        Values are numeric or None on failure.
        """
        mapping = [
            (1, 'Temperature'),
            (2, 'Humidity'),
            (3, 'Pressure'),
            (4, 'CO2_Level'),
            (5, 'Occupancy'),
        ]
        results = {}
        for instance, name in mapping:
            try:
                val = client_obj.read_analog(target, 'analogValue', instance)
                results[name] = val
            except Exception as e:
                log.debug(f"Error reading {name} ({instance}): {e}")
                results[name] = None
        return results

    try:
        client.start()
        print("Client started. Polling sensors on 127.0.0.1:47808 (Ctrl-C to stop)...")
        while True:
            readings = read_all_sensors(client, '127.0.0.1:47808')
            now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            # Prepare formatted output, using sensible units
            t = readings.get('Temperature')
            h = readings.get('Humidity')
            p = readings.get('Pressure')
            c = readings.get('CO2_Level')
            o = readings.get('Occupancy')

            def fmt_num(x, digs=2):
                return f"{x:.{digs}f}" if (x is not None) else "N/A"

            occ_str = str(int(o)) if (o is not None) else "N/A"

            line = (
                f"[{now}] [SENSOR] Temp:  {fmt_num(t)}°C | "
                f"Humidity:  {fmt_num(h)}% | "
                f"Pressure: {fmt_num(p)}hPa | "
                f"CO2:   {fmt_num(c)}ppm | "
                f"Occupancy:  {occ_str}"
            )
            print(line)

            time.sleep(1.0)
    except KeyboardInterrupt:
        print('\nStopping client...')
    finally:
        try:
            if client.db is not None:
                client.db.close()
        except Exception:
            pass
        client.stop()
