"""
BMS Simulator - Complete Demonstration
Shows how to use the BMS device, BACnet server, and client together
"""

import time
import logging
from bms_simulator import BMSDevice
from bms_bacnet_server import BMSBACnetServer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def demo_bms_only():
    """Demonstrate BMS device standalone (without BACnet)"""
    print("\n" + "="*70)
    print("DEMO 1: BMS Device Standalone Operation")
    print("="*70 + "\n")
    
    # Create and start BMS device
    bms = BMSDevice(
        device_id="BMS-DEMO-01",
        location="Building A - Conference Room"
    )
    
    # Display device info
    print(f"Device Info: {bms.get_device_info()}\n")
    
    # Start simulation
    bms.start_simulation(update_interval=1.0)
    print("Simulation started. Reading sensors...\n")
    
    # Read and display sensor data
    try:
        for cycle in range(5):
            time.sleep(1)
            data = bms.get_sensor_data()
            
            print(f"--- Cycle {cycle + 1} ---")
            for sensor_name, value in data.items():
                metadata = bms.get_sensor_metadata(sensor_name)
                unit = metadata['unit']
                print(f"  {sensor_name:15} : {value:8.2f} {unit}")
            
            if cycle < 4:
                print()
    
    except KeyboardInterrupt:
        print("\nInterrupted")
    finally:
        bms.stop_simulation()
        print("\nBMS simulation stopped\n")


def demo_bms_with_server():
    """Demonstrate BMS with BACnet server"""
    print("\n" + "="*70)
    print("DEMO 2: BMS Device with BACnet Server")
    print("="*70 + "\n")
    
    # Create BMS device
    bms = BMSDevice(
        device_id="BMS-DEMO-02",
        location="Building B - Server Room"
    )
    
    # Start simulation
    print("Starting BMS simulation...")
    bms.start_simulation(update_interval=0.5)
    time.sleep(1)
    
    # Create and start BACnet server
    print("Initializing BACnet server...")
    server = BMSBACnetServer(
        bms_device=bms,
        device_id=12345,
        device_name="BMS-Server-Demo",
        local_address="192.168.1.100/24:47808"
    )
    
    # Initialize the server
    if server.initialize():
        print("BACnet server initialized successfully!")
        print(f"Server Info: {server.get_device_info()}\n")
        
        # Start the server
        server.start()
        time.sleep(1)
        
        print("BACnet server is running...\n")
        
        try:
            # Display server-provided data
            for cycle in range(5):
                time.sleep(1)
                print(f"--- Reading Cycle {cycle + 1} ---")
                
                for i, sensor_name in enumerate(['temperature', 'humidity', 'pressure', 'co2_level', 'occupancy']):
                    try:
                        value = server.get_sensor_value(sensor_name)
                        metadata = bms.get_sensor_metadata(sensor_name)
                        unit = metadata['unit']
                        
                        if value is not None:
                            print(f"  {sensor_name:15} : {value:8.2f} {unit}")
                        else:
                            print(f"  {sensor_name:15} : No data")
                    
                    except Exception as e:
                        print(f"  {sensor_name:15} : Error - {e}")
                
                if cycle < 4:
                    print()
        
        except KeyboardInterrupt:
            print("\nInterrupted")
        finally:
            server.stop()
            bms.stop_simulation()
            print("\nServer and simulation stopped\n")
    
    else:
        print("Failed to initialize BACnet server\n")
        bms.stop_simulation()


def demo_sensor_control():
    """Demonstrate manual sensor control"""
    print("\n" + "="*70)
    print("DEMO 3: Manual Sensor Control")
    print("="*70 + "\n")
    
    # Create BMS device
    bms = BMSDevice(
        device_id="BMS-DEMO-03",
        location="Building C - Test Lab"
    )
    
    print("BMS Device without automatic simulation\n")
    
    # Manually set sensor values
    sensor_values = {
        'temperature': 23.5,
        'humidity': 45.0,
        'pressure': 1013.25,
        'co2_level': 450.0,
        'occupancy': 25
    }
    
    print("Setting sensor values manually:")
    for sensor, value in sensor_values.items():
        bms.set_sensor_value(sensor, value)
    
    print("\nReading current sensor values:")
    data = bms.get_sensor_data()
    for sensor_name, value in data.items():
        metadata = bms.get_sensor_metadata(sensor_name)
        unit = metadata['unit']
        range_min, range_max = metadata['range']
        print(f"  {sensor_name:15} : {value:8.2f} {unit:>10} (range: {range_min}-{range_max})")
    
    print()


def demo_multiple_bms_devices():
    """Demonstrate multiple BMS devices"""
    print("\n" + "="*70)
    print("DEMO 4: Multiple BMS Devices")
    print("="*70 + "\n")
    
    # Create multiple BMS devices
    devices = [
        BMSDevice(device_id="BMS-FL01", location="Building A - Floor 1"),
        BMSDevice(device_id="BMS-FL02", location="Building A - Floor 2"),
        BMSDevice(device_id="BMS-FL03", location="Building A - Floor 3"),
    ]
    
    # Start simulations
    print("Starting simulations for multiple floors...\n")
    for device in devices:
        device.start_simulation(update_interval=1.0)
    
    try:
        for cycle in range(3):
            print(f"--- Cycle {cycle + 1} ---")
            
            for device in devices:
                data = device.get_sensor_data()
                info = device.get_device_info()
                
                # Display key metrics for each device
                temp = data['temperature']
                co2 = data['co2_level']
                occupancy = data['occupancy']
                
                print(f"{info['device_id']:10} ({info['location']:30}): "
                      f"Temp={temp:6.1f}°C, CO2={co2:6.0f}ppm, Occupancy={occupancy:2.0f}")
            
            if cycle < 2:
                print()
            time.sleep(1)
    
    except KeyboardInterrupt:
        print("\nInterrupted")
    finally:
        for device in devices:
            device.stop_simulation()
        print("\nAll simulations stopped\n")


def print_menu():
    """Print demo menu"""
    print("\n" + "="*70)
    print("BMS SIMULATOR - DEMONSTRATION MENU")
    print("="*70)
    print("1. BMS Device Standalone (no BACnet)")
    print("2. BMS with BACnet Server")
    print("3. Manual Sensor Control")
    print("4. Multiple BMS Devices")
    print("5. Run All Demos")
    print("0. Exit")
    print("="*70 + "\n")


def main():
    """Main demonstration function"""
    demos = {
        '1': ('BMS Device Standalone', demo_bms_only),
        '2': ('BMS with BACnet Server', demo_bms_with_server),
        '3': ('Manual Sensor Control', demo_sensor_control),
        '4': ('Multiple BMS Devices', demo_multiple_bms_devices),
        '5': ('All Demos', lambda: [
            demo_bms_only(),
            demo_bms_with_server(),
            demo_sensor_control(),
            demo_multiple_bms_devices()
        ])
    }
    
    while True:
        print_menu()
        choice = input("Select demo (0-5): ").strip()
        
        if choice == '0':
            print("Exiting...\n")
            break
        
        if choice in demos:
            name, demo_func = demos[choice]
            print(f"\nRunning: {name}")
            try:
                demo_func()
            except Exception as e:
                print(f"Error running demo: {e}")
                logger.exception("Demo error")
        else:
            print("Invalid choice. Please try again.")
        
        if choice != '5':  # Don't ask for confirmation after "All Demos"
            input("\nPress Enter to continue...")


if __name__ == "__main__":
    print("\nWelcome to BMS Simulator Demonstration\n")
    
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nDemo terminated by user")
    except Exception as e:
        print(f"\nFatal error: {e}")
        logger.exception("Fatal error")
