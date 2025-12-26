"""
BMS System Test Suite - Quick validation of all components
"""

import time
import logging
from bms_simulator import BMSDevice
from bms_bacnet_server import BMSServer
from bms_bacnet_client import BMSClient

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


def test_bms_device():
    """Test BMS Device"""
    print("\n" + "="*60)
    print("TEST 1: BMS Device")
    print("="*60 + "\n")
    
    try:
        # Create device
        device = BMSDevice(device_id="TEST-01", location="Test Lab")
        print("✓ Device creation")
        
        # Get device info
        info = device.get_device_info()
        assert info['device_id'] == "TEST-01"
        print("✓ Device info retrieval")
        
        # Start simulation
        device.start_simulation(update_interval=0.5)
        assert device.running
        print("✓ Simulation started")
        
        # Read sensor data
        time.sleep(1)
        data = device.get_sensor_data()
        assert all(k in data for k in ['temperature', 'humidity', 'pressure', 'co2_level', 'occupancy'])
        print("✓ Sensor data reading")
        
        # Test metadata
        metadata = device.get_sensor_metadata('temperature')
        assert 'unit' in metadata and 'range' in metadata
        print("✓ Sensor metadata")
        
        # Manual control
        device.set_sensor_value('temperature', 23.5)
        temp = device.get_sensor_value('temperature')
        assert abs(temp - 23.5) < 0.1
        print("✓ Manual sensor control")
        
        # Stop simulation
        device.stop_simulation()
        assert not device.running
        print("✓ Simulation stopped")
        
        print("\n✓ All BMS Device tests passed!")
        return True
    
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        return False
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        logger.exception("Error")
        return False


def test_server():
    """Test BMS Server"""
    print("\n" + "="*60)
    print("TEST 2: BMS Server")
    print("="*60 + "\n")
    
    try:
        # Create and start device
        device = BMSDevice(device_id="TEST-02", location="Test")
        device.start_simulation(update_interval=0.5)
        time.sleep(1)
        print("✓ Test device created and running")
        
        # Create server
        server = BMSServer(
            bms_device=device,
            device_id=12345,
            device_name="TEST-Server",
            host="127.0.0.1",
            port=47808
        )
        print("✓ Server creation")
        
        # Initialize
        assert server.initialize()
        print("✓ Server initialization")
        
        # Check info
        info = server.get_device_info()
        assert info['device_name'] == "TEST-Server"
        assert len(server.sensor_objects) == 5
        print("✓ Server info and objects")
        
        # Start server
        server.start()
        time.sleep(1)
        print("✓ Server started")
        
        # Check sensor values
        temp = server.get_sensor_value('temperature')
        assert temp is not None and isinstance(temp, (int, float))
        print("✓ Sensor value reading")
        
        # Stop
        server.stop()
        device.stop_simulation()
        print("✓ Server and device stopped")
        
        print("\n✓ All Server tests passed!")
        return True
    
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        return False
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        logger.exception("Error")
        return False


def test_client():
    """Test BMS Client"""
    print("\n" + "="*60)
    print("TEST 3: BMS Client")
    print("="*60 + "\n")
    
    try:
        # Create client
        client = BMSClient(host="127.0.0.1", port=47808)
        assert client.host == "127.0.0.1"
        assert client.port == 47808
        print("✓ Client creation")
        
        # Check representation
        repr_str = repr(client)
        assert "BMSClient" in repr_str
        print("✓ Client representation")
        
        # Check context manager
        with BMSClient(host="127.0.0.1", port=47808) as ctx_client:
            assert ctx_client is not None
        print("✓ Context manager support")
        
        print("\n✓ All Client tests passed!")
        return True
    
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        return False
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        logger.exception("Error")
        return False


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("BMS SYSTEM TEST SUITE")
    print("="*60)
    
    results = [
        ("BMS Device", test_bms_device()),
        ("BMS Server", test_server()),
        ("BMS Client", test_client()),
    ]
    
    # Summary
    print("\n" + "="*60)
    print("FINAL RESULTS")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status:8} - {name}")
    
    print(f"\nTotal: {passed}/{total} passed ({100*passed/total:.0f}%)")
    print("="*60 + "\n")
    
    return 0 if passed == total else 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
