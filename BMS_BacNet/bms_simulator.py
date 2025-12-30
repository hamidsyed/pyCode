"""
Building Management System (BMS) Simulator
Simulates a BMS device with 6 sensor parameters and BACnet protocol support
"""

import time
import random
import threading
from typing import Dict
import logging
from weatherClass import weatherClass

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class BMSDevice:
    """
    Building Management System Device Simulator
    Simulates 6 sensor parameters:
    1. Total Electricity Energy (kWh)
    2. Outdoor Air Drybulb Temperature (°C)
    3. Outdoor Air Relative Humidity (%)
    4. Wind Speed (m/s)
    5. Diffuse Solar Radiation (W/m²)
    6. Direct Solar Radiation (W/m²)
    """

    # Delhi's coordinates
    delhi_lat = 28.61
    delhi_lon = 77.23
    weather_provider = weatherClass(latitude=delhi_lat, longitude=delhi_lon)

    # Get the current weather data
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
            'electricity_energy': 0.0,           # kWh (cumulative, 0-600 kWh)
            'outdoor_temp': 20.0,                # °C (5-44°C range)
            'outdoor_humidity': 50.0,            # % (11-100% range)
            'wind_speed': 2.0,                   # m/s (0-9.3 m/s range)
            'diffuse_solar': 150.0,              # W/m² (0-444 W/m² range)
            'direct_solar': 400.0                # W/m² (0-924 W/m² range)
        }
        
        # Sensor metadata
        self.sensor_metadata = {
            'electricity_energy': {'unit': 'kWh', 'range': (0, 600), 'precision': 0.1},
            'outdoor_temp': {'unit': '°C', 'range': (5, 44), 'precision': 0.1},
            'outdoor_humidity': {'unit': '%', 'range': (11, 100), 'precision': 0.5},
            'wind_speed': {'unit': 'm/s', 'range': (0, 9.3), 'precision': 0.1},
            'diffuse_solar': {'unit': 'W/m²', 'range': (0, 444), 'precision': 1.0},
            'direct_solar': {'unit': 'W/m²', 'range': (0, 924), 'precision': 1.0}
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
    
    
        # Create an instance of weatherClass
        weather_data = BMSDevice.weather_provider.get_current_weather()
        """""
        print(f"Weather in Delhi (Lat: {weather_data['latitude']}, Lon: {weather_data['longitude']}) for {weather_data['current_time']}:")
        print(f"Temperature: {weather_data['temperature']}°C")
        print(f"Relative Humidity: {weather_data['relative_humidity']}%")
        print(f"Wind Speed: {weather_data['wind_speed']} m/s")
        print(f"Diffuse Solar Radiation: {weather_data['diffuse_radiation']} W/m²")
        print(f"Direct Solar Radiation: {weather_data['direct_radiation']} W/m²")
        print(f"Weather Code: {weather_data['weather_code']}")
        print("\nNote: 'Total Electricity Energy (kWh)' is not available via Open-Meteo API.")
        """
        with self.data_lock:
            # Electricity Energy: cumulative, always increasing (simulates consumption)
            # Increment by 0.01-0.05 kWh per update (realistic for building consumption)
            energy_increment = random.uniform(0.01, 0.05)
            self.sensor_data['electricity_energy'] = min(600, 
                self.sensor_data['electricity_energy'] + energy_increment)
            
            # Outdoor Temperature: gradual changes simulating daily patterns
            #temp_change = random.gauss(0, 0.5)
            #self.sensor_data['outdoor_temp'] = max(5, min(44, self.sensor_data['outdoor_temp'] + temp_change))
            self.sensor_data['outdoor_temp'] = weather_data['temperature']
            
            # Outdoor Humidity: inverse correlation with temperature + random variation
            #humidity_change = random.gauss(-0.3, 1.0)
            #self.sensor_data['outdoor_humidity'] = max(11, min(100,
            #    self.sensor_data['outdoor_humidity'] + humidity_change))
            self.sensor_data['outdoor_humidity'] = weather_data['relative_humidity']
            
            # Wind Speed: random gusts and calm periods
            #wind_change = random.gauss(0, 0.3)
            #self.sensor_data['wind_speed'] = max(0, min(9.3,
            #    self.sensor_data['wind_speed'] + wind_change))
            self.sensor_data['wind_speed'] = weather_data['wind_speed']

            # Diffuse Solar Radiation: varies with time and weather conditions
            # Simulates cloud cover and atmospheric scattering
            #diffuse_change = random.gauss(0, 10)
            #self.sensor_data['diffuse_solar'] = max(0, min(444,
            #    self.sensor_data['diffuse_solar'] + diffuse_change))
            self.sensor_data['diffuse_solar'] = weather_data['diffuse_radiation']
            
            # Direct Solar Radiation: varies with sun position and weather
            # Higher values during clear sky conditions
            #direct_change = random.gauss(0, 20)
            #self.sensor_data['direct_solar'] = max(0, min(924,
            #    self.sensor_data['direct_solar'] + direct_change))
            self.sensor_data['direct_solar'] = weather_data['direct_radiation']

            
            # Print current sensor data to stdout with timestamp
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            print(f"[{timestamp}] [SENSOR] Energy: {self.sensor_data['electricity_energy']:6.2f}kWh | "
                  f"OutTemp: {self.sensor_data['outdoor_temp']:5.1f}°C | "
                  f"OutHum: {self.sensor_data['outdoor_humidity']:5.1f}% | "
                  f"Wind: {self.sensor_data['wind_speed']:4.1f}m/s | "
                  f"DiffSolar: {self.sensor_data['diffuse_solar']:6.1f}W/m² | "
                  f"DirSolar: {self.sensor_data['direct_solar']:6.1f}W/m²")
    
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
    bms.start_simulation(update_interval=5.0)
    
    # Display sensor readings for 10 seconds
    try:
        #for i in range(10):
        i = 0
        while True:
            time.sleep(5)
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
