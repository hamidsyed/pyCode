"""
Building Management System (BMS) Simulator
Simulates a BMS device with 5 sensor parameters and BACnet protocol support
"""

import time
import random
import threading
from typing import Dict
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class BMSDevice:
    """
    Building Management System Device Simulator
    Simulates 5 sensor parameters:
    1. Temperature (Celsius)
    2. Humidity (Percentage)
    3. Atmospheric Pressure (hPa)
    4. CO2 Level (ppm)
    5. Occupancy (number of people)
    """
    
    def __init__(self, device_id: str = "BMS-001", location: str = "Building A"):
        """
        Initialize BMS Device
        
        Args:
            device_id: Unique identifier for the device
            location: Physical location of the device
        """
        self.device_id = device_id
        self.location = location
        self.running = False
        self.simulation_thread = None
        
        # Sensor data storage with realistic initial values
        self.sensor_data = {
            'temperature': 22.0,      # Celsius (18-26°C typical range)
            'humidity': 45.0,          # Percentage (30-60% typical range)
            'pressure': 1013.25,       # hPa (barometric pressure)
            'co2_level': 400.0,        # ppm (parts per million)
            'occupancy': 10            # Number of people
        }
        
        # Sensor metadata
        self.sensor_metadata = {
            'temperature': {'unit': '°C', 'range': (18, 26), 'precision': 0.5},
            'humidity': {'unit': '%', 'range': (30, 60), 'precision': 1.0},
            'pressure': {'unit': 'hPa', 'range': (990, 1030), 'precision': 0.1},
            'co2_level': {'unit': 'ppm', 'range': (300, 1000), 'precision': 10.0},
            'occupancy': {'unit': 'count', 'range': (0, 100), 'precision': 1}
        }
        
        # Lock for thread-safe access
        self.data_lock = threading.RLock()
        
        logger.info(f"BMS Device initialized: {device_id} at {location}")
    
    def start_simulation(self, update_interval: float = 1.0):
        """
        Start the sensor simulation
        
        Args:
            update_interval: Time in seconds between sensor updates
        """
        if self.running:
            logger.warning("Simulation already running")
            return
        
        self.running = True
        self.simulation_thread = threading.Thread(
            target=self._simulation_loop,
            args=(update_interval,),
            daemon=True
        )
        self.simulation_thread.start()
        logger.info(f"Simulation started with {update_interval}s update interval")
    
    def stop_simulation(self):
        """Stop the sensor simulation"""
        self.running = False
        if self.simulation_thread:
            self.simulation_thread.join(timeout=5)
        logger.info("Simulation stopped")
    
    def _simulation_loop(self, update_interval: float):
        """
        Continuous simulation loop that updates sensor values
        
        Args:
            update_interval: Time in seconds between updates
        """
        while self.running:
            self._update_sensors()
            time.sleep(update_interval)
    
    def _update_sensors(self):
        """Update sensor values with realistic variations"""
        with self.data_lock:
            # Temperature: gradual changes with occasional spikes
            temp_change = random.gauss(0, 0.3)
            self.sensor_data['temperature'] = max(18, min(26, 
                self.sensor_data['temperature'] + temp_change))
            
            # Humidity: inverse correlation with temperature + random variation
            humidity_change = random.gauss(-0.2, 0.5)
            self.sensor_data['humidity'] = max(30, min(60,
                self.sensor_data['humidity'] + humidity_change))
            
            # Pressure: small variations (weather simulation)
            pressure_change = random.gauss(0, 0.5)
            self.sensor_data['pressure'] = max(990, min(1030,
                self.sensor_data['pressure'] + pressure_change))
            
            # CO2 Level: increases with occupancy, decreases with ventilation
            occupancy_factor = self.sensor_data['occupancy'] / 20.0
            co2_change = random.gauss(occupancy_factor, 5)
            self.sensor_data['co2_level'] = max(300, min(1000,
                self.sensor_data['co2_level'] + co2_change))
            
            # Occupancy: random changes (people entering/leaving)
            if random.random() < 0.3:  # 30% chance of change each cycle
                occupancy_change = random.randint(-5, 5)
                self.sensor_data['occupancy'] = max(0, min(100,
                    self.sensor_data['occupancy'] + occupancy_change))
            
            # Print current sensor data to stdout with timestamp
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            print(f"[{timestamp}] [SENSOR] Temp: {self.sensor_data['temperature']:6.2f}°C | "
                  f"Humidity: {self.sensor_data['humidity']:5.1f}% | "
                  f"Pressure: {self.sensor_data['pressure']:7.2f}hPa | "
                  f"CO2: {self.sensor_data['co2_level']:7.1f}ppm | "
                  f"Occupancy: {self.sensor_data['occupancy']:3.0f}")
    
    def get_sensor_data(self) -> Dict[str, float]:
        """
        Get current sensor data
        
        Returns:
            Dictionary of sensor readings
        """
        with self.data_lock:
            return self.sensor_data.copy()
    
    def get_sensor_value(self, sensor_name: str) -> float:
        """
        Get a specific sensor value
        
        Args:
            sensor_name: Name of the sensor
            
        Returns:
            Sensor reading value
        """
        with self.data_lock:
            if sensor_name not in self.sensor_data:
                raise ValueError(f"Unknown sensor: {sensor_name}")
            return self.sensor_data[sensor_name]
    
    def get_sensor_metadata(self, sensor_name: str) -> Dict:
        """
        Get metadata for a sensor
        
        Args:
            sensor_name: Name of the sensor
            
        Returns:
            Sensor metadata (unit, range, precision)
        """
        if sensor_name not in self.sensor_metadata:
            raise ValueError(f"Unknown sensor: {sensor_name}")
        return self.sensor_metadata[sensor_name].copy()
    
    def get_device_info(self) -> Dict:
        """
        Get device information
        
        Returns:
            Device metadata
        """
        return {
            'device_id': self.device_id,
            'location': self.location,
            'sensors': list(self.sensor_data.keys()),
            'running': self.running
        }
    
    def set_sensor_value(self, sensor_name: str, value: float):
        """
        Manually set a sensor value (for testing)
        
        Args:
            sensor_name: Name of the sensor
            value: Value to set
        """
        with self.data_lock:
            if sensor_name not in self.sensor_data:
                raise ValueError(f"Unknown sensor: {sensor_name}")
            
            # Clamp value to valid range
            metadata = self.sensor_metadata[sensor_name]
            min_val, max_val = metadata['range']
            self.sensor_data[sensor_name] = max(min_val, min(max_val, value))
            logger.info(f"Manually set {sensor_name} to {value}")
    
    def __repr__(self) -> str:
        return f"BMSDevice({self.device_id}, {self.location})"


if __name__ == "__main__":
    # Example usage
    bms = BMSDevice(device_id="BMS-OFFICE-01", location="Office Building - Floor 3")
    
    # Start simulation
    bms.start_simulation(update_interval=1.0)
    
    # Display sensor readings for 10 seconds
    try:
        #for i in range(10):
        i = 0
        while True:
            time.sleep(1)
            data = bms.get_sensor_data()
            print(f"\n--- Sensor Reading {i+1} ---")
            for sensor, value in data.items():
                metadata = bms.get_sensor_metadata(sensor)
                print(f"{sensor:15} : {value:8.2f} {metadata['unit']}")
            i += 1
    except KeyboardInterrupt:
        print("\nInterrupted by user")
    finally:
        bms.stop_simulation()
