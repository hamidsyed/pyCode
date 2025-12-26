"""
BACnet-based BMS Client (bacpypes)

This client demonstrates how to read `presentValue` from AnalogValue objects
exposed by the `bms_bacnet_server_bacnet.py` server using `bacpypes`.

Note: bacpypes networking API can be low-level. The example below uses a
simple synchronous request/response pattern. For robust production use you
should follow bacpypes examples and handle retries/timeouts properly.

Usage:
    from bms_bacnet_client_bacnet import BACnetBMSClient
    client = BACnetBMSClient(local_device_id=999, local_address='0.0.0.0/47809')
    client.start()
    val = client.read_analog('127.0.0.1/47808', 'analogValue', 1)
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

    def __init__(self, local_device_id=999, local_address="0.0.0.0/47809", db_config: Optional[Dict[str, Any]] = None):
        if not BACPYPES_AVAILABLE:
            raise ImportError(
                "bacpypes is required for BACnet implementation. "
                "Install with: pip install bacpypes (use Python 3.11 recommended)"
            )
        self.local_device = LocalDeviceObject(
            objectName=f"BMSClient-{local_device_id}", objectIdentifier=local_device_id
        )
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

    def read_analog(self, target_address, object_type, instance, timeout=2.0):
        """Read presentValue from a remote analogValue instance.

        target_address: 'host/port' string, e.g. '127.0.0.1/47808'
        object_type: typically 'analogValue'
        instance: integer instance number
        """
        addr = Address(target_address)
        # Build ReadPropertyRequest
        request = ReadPropertyRequest(
            objectIdentifier=(object_type, int(instance)),
            propertyIdentifier='presentValue',
        )
        request.pduDestination = addr

        # send and wait for response via application
        try:
            iocb = self.app.request_io(request)
            iocb.wait(timeout)
            if iocb.ioError:
                raise iocb.ioError
            if iocb.ioResponse is None:
                raise RuntimeError("No response received")
            # read value from response
            resp = iocb.ioResponse
            # property value may be in resp.propertyValue
            # the exact structure depends on bacpypes version
            try:
                # Many examples put the value in resp.propertyValue[0].propertyValue
                pv = resp.propertyValue[0].propertyValue
            except Exception:
                # fallback: try presentValue attribute
                pv = getattr(resp, 'presentValue', None)
            # convert pv to a primitive value if possible
            value_to_store = None
            try:
                # many bacpypes types implement __float__ or .value
                value_to_store = float(pv)
            except Exception:
                try:
                    # try attribute 'value' or 'presentValue'
                    value_to_store = float(getattr(pv, 'value', getattr(pv, 'presentValue', pv)))
                except Exception:
                    # fallback to string representation
                    value_to_store = str(pv)

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

            return pv
        except Exception as e:
            log.exception("BACnet read failed: %s", e)
            raise


if __name__ == "__main__":
    import threading
    try:
        from bms_simulator import BMSDevice
    except Exception:
        print("This demo requires bms_simulator.py in the same folder")
        raise

    # Simple run-through: start client and perform sample reads
    client = BACnetBMSClient(local_device_id=999, local_address='0.0.0.0/47809')
    try:
        client.start()
        print('Client running. Read example (may fail if no server is running):')
        try:
            v = client.read_analog('127.0.0.1/47808', 'analogValue', 1)
            print('Read result:', v)
        except Exception as e:
            print('Read failed:', e)
    finally:
        client.stop()
