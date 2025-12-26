"""
Complete BMS System Example
Demonstrates server and client working together in a single script
"""

import logging
import time
import json
import threading
from bms_simulator import BMSDevice
from bms_bacnet_server import BMSServer
from bms_bacnet_client import BMSClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def run_server(duration: float = 30):
    """Run BMS server with simulator"""
    logger.info("Starting BMS server with simulator...")
    
    # Create and start BMS device
    bms = BMSDevice(
        device_id="BMS-DEMO-01",
        location="Building A - Floor 3"
    )
    bms.start_simulation(update_interval=1.0)
    
    # Create and start server
    server = BMSServer(
        bms_device=bms,
        device_id=12345,
        device_name="BMS-Demo-Server",
        host="127.0.0.1",
        port=47808
    )
    
    if not server.initialize():
        logger.error("Failed to initialize server")
        return
    
    server.start()
    logger.info(f"Server running on 127.0.0.1:47808")
    
    try:
        # Keep server running
        time.sleep(duration)
    except KeyboardInterrupt:
        logger.info("Server interrupted by user")
    finally:
        server.stop()
        bms.stop_simulation()
        logger.info("Server shutdown complete")


def run_client():
    """Run BMS client to read data"""
    time.sleep(2)  # Wait for server to start
    
    logger.info("Starting BMS client...")
    
    client = BMSClient(
        host="127.0.0.1",
        port=47808,
        timeout=10
    )
    
    # Try to read data
    successful_reads = 0
    
    for i in range(5):
        try:
            if not client.connected:
                if not client.connect():
                    logger.warning(f"Attempt {i+1}: Failed to connect to server")
                    time.sleep(1)
                    continue
            
            # Read all sensor data
            logger.info(f"\n--- Reading Cycle {i+1} ---")
            data = client.read_all_sensors()
            
            if data:
                successful_reads += 1
                logger.info("Sensor Data:")
                for sensor_name, value in data.items():
                    logger.info(f"  {sensor_name:15} : {value:8.2f}")
            else:
                logger.warning("No data received from server")
            
            time.sleep(2)
        
        except Exception as e:
            logger.error(f"Error reading data: {e}")
            time.sleep(1)
    
    client.disconnect()
    logger.info(f"\nClient completed: {successful_reads}/5 successful reads")


def demo_with_threads():
    """Run server and client in parallel threads"""
    print("\n" + "="*70)
    print("BMS SYSTEM - INTEGRATED DEMO (Server + Client)")
    print("="*70 + "\n")
    
    # Start server in background thread
    server_thread = threading.Thread(
        target=run_server,
        args=(30,),
        daemon=True
    )
    server_thread.start()
    logger.info("Server thread started")
    
    # Start client in main thread
    try:
        run_client()
    except KeyboardInterrupt:
        logger.info("Demo interrupted by user")
    finally:
        server_thread.join(timeout=5)
        logger.info("Demo completed")


def demo_simple_monitor():
    """Simple monitoring example"""
    print("\n" + "="*70)
    print("BMS SYSTEM - SIMPLE MONITORING")
    print("="*70 + "\n")
    
    # Create device
    bms = BMSDevice(
        device_id="MONITOR-01",
        location="Conference Room"
    )
    
    logger.info("Monitoring BMS device for 10 seconds...\n")
    bms.start_simulation(update_interval=0.5)
    
    # Collect statistics
    readings = {sensor: [] for sensor in ['temperature', 'humidity', 'pressure', 'co2_level', 'occupancy']}
    
    try:
        for cycle in range(10):
            data = bms.get_sensor_data()
            
            for sensor, value in data.items():
                readings[sensor].append(float(value))
            
            if (cycle + 1) % 5 == 0:
                logger.info(f"Cycle {cycle + 1}: Data collected")
            
            time.sleep(1)
    
    finally:
        bms.stop_simulation()
    
    # Print statistics
    print("\n" + "-"*70)
    print("SENSOR STATISTICS")
    print("-"*70 + "\n")
    
    for sensor, values in readings.items():
        if values:
            metadata = bms.get_sensor_metadata(sensor)
            unit = metadata['unit']
            
            print(f"{sensor} ({unit}):")
            print(f"  Min:     {min(values):8.2f}")
            print(f"  Max:     {max(values):8.2f}")
            print(f"  Average: {sum(values)/len(values):8.2f}")
            print()


def demo_manual_control():
    """Example of manual sensor control"""
    print("\n" + "="*70)
    print("BMS SYSTEM - MANUAL SENSOR CONTROL")
    print("="*70 + "\n")
    
    # Create device without simulation
    bms = BMSDevice(
        device_id="MANUAL-01",
        location="Lab Test"
    )
    
    logger.info("Testing manual sensor control\n")
    
    # Test scenarios
    scenarios = [
        {
            'name': 'Normal Conditions',
            'temperature': 22.0,
            'humidity': 45.0,
            'pressure': 1013.25,
            'co2_level': 400.0,
            'occupancy': 20
        },
        {
            'name': 'High Temperature',
            'temperature': 28.0,
            'humidity': 60.0,
            'pressure': 1010.0,
            'co2_level': 500.0,
            'occupancy': 40
        },
        {
            'name': 'Low Occupancy',
            'temperature': 18.0,
            'humidity': 35.0,
            'pressure': 1015.0,
            'co2_level': 350.0,
            'occupancy': 2
        }
    ]
    
    for scenario in scenarios:
        print(f"\nScenario: {scenario['name']}")
        print("-" * 50)
        
        # Set sensor values
        for sensor, value in scenario.items():
            if sensor != 'name':
                bms.set_sensor_value(sensor, value)
        
        # Read and display
        data = bms.get_sensor_data()
        for sensor, value in data.items():
            metadata = bms.get_sensor_metadata(sensor)
            unit = metadata['unit']
            print(f"  {sensor:15} : {value:8.2f} {unit}")


def main():
    """Main demo selector"""
    print("\n" + "="*70)
    print("BMS SYSTEM - COMPLETE DEMONSTRATION")
    print("="*70 + "\n")
    
    print("Select demo to run:")
    print("1. Integrated Server + Client (with threading)")
    print("2. Simple Monitoring")
    print("3. Manual Sensor Control")
    print("4. Run All Demos")
    print("0. Exit\n")
    
    choice = input("Enter choice (0-4): ").strip()
    
    if choice == '1':
        demo_with_threads()
    elif choice == '2':
        demo_simple_monitor()
    elif choice == '3':
        demo_manual_control()
    elif choice == '4':
        demo_with_threads()
        demo_simple_monitor()
        demo_manual_control()
    elif choice == '0':
        print("Exiting...")
        return
    else:
        print("Invalid choice")
        return
    
    print("\n" + "="*70)
    print("Demo completed successfully!")
    print("="*70 + "\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user")
    except Exception as e:
        logger.exception("Unexpected error")
