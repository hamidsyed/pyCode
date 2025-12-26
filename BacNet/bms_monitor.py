"""
BMS Monitoring System
Advanced example showing logging, analysis, and alerts
"""

import json
import csv
import time
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from bms_simulator import BMSDevice

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class SensorReading:
    """Container for a sensor reading"""
    timestamp: str
    device_id: str
    sensor_name: str
    value: float
    unit: str
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return asdict(self)


class BMSMonitor:
    """
    Monitoring system for BMS devices
    Logs data, generates statistics, and detects anomalies
    """
    
    def __init__(self, output_dir: str = "./bms_logs"):
        """
        Initialize monitor
        
        Args:
            output_dir: Directory for storing logs and data
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        self.readings: List[SensorReading] = []
        self.devices: Dict[str, BMSDevice] = {}
        self.running = False
        
        # Alert thresholds
        self.thresholds = {
            'temperature': {'min': 18, 'max': 26, 'name': 'Temperature'},
            'humidity': {'min': 30, 'max': 60, 'name': 'Humidity'},
            'pressure': {'min': 990, 'max': 1030, 'name': 'Pressure'},
            'co2_level': {'min': 300, 'max': 1000, 'name': 'CO2 Level'},
            'occupancy': {'min': 0, 'max': 100, 'name': 'Occupancy'}
        }
        
        logger.info(f"BMS Monitor initialized with output directory: {self.output_dir}")
    
    def add_device(self, device: BMSDevice):
        """
        Register a BMS device for monitoring
        
        Args:
            device: BMSDevice instance
        """
        self.devices[device.device_id] = device
        logger.info(f"Device {device.device_id} added to monitor")
    
    def start_monitoring(self, interval: float = 5.0, duration: Optional[float] = None):
        """
        Start monitoring devices
        
        Args:
            interval: Time between readings in seconds
            duration: Total monitoring duration (None = infinite)
        """
        self.running = True
        start_time = time.time()
        
        logger.info(f"Starting monitoring with {interval}s interval")
        
        try:
            while self.running:
                # Check if duration limit reached
                if duration and (time.time() - start_time) > duration:
                    logger.info("Monitoring duration limit reached")
                    break
                
                # Collect readings from all devices
                for device_id, device in self.devices.items():
                    try:
                        self._collect_readings(device)
                    except Exception as e:
                        logger.error(f"Error collecting readings from {device_id}: {e}")
                
                time.sleep(interval)
        
        except Exception as e:
            logger.error(f"Error in monitoring loop: {e}")
        finally:
            self.running = False
            logger.info("Monitoring stopped")
    
    def _collect_readings(self, device: BMSDevice):
        """
        Collect sensor readings from a device
        
        Args:
            device: BMSDevice instance
        """
        data = device.get_sensor_data()
        timestamp = datetime.now().isoformat()
        
        for sensor_name, value in data.items():
            try:
                metadata = device.get_sensor_metadata(sensor_name)
                unit = metadata['unit']
                
                reading = SensorReading(
                    timestamp=timestamp,
                    device_id=device.device_id,
                    sensor_name=sensor_name,
                    value=value,
                    unit=unit
                )
                
                self.readings.append(reading)
                
                # Check for anomalies
                self._check_thresholds(reading, device)
            
            except Exception as e:
                logger.error(f"Error collecting {sensor_name}: {e}")
    
    def _check_thresholds(self, reading: SensorReading, device: BMSDevice):
        """
        Check if reading exceeds thresholds
        
        Args:
            reading: SensorReading instance
            device: BMSDevice instance
        """
        if reading.sensor_name not in self.thresholds:
            return
        
        threshold = self.thresholds[reading.sensor_name]
        min_val, max_val = threshold['min'], threshold['max']
        
        if reading.value < min_val or reading.value > max_val:
            alert_msg = (
                f"ALERT [{reading.device_id}] {threshold['name']}: "
                f"{reading.value:.2f} {reading.unit} "
                f"(range: {min_val}-{max_val})"
            )
            logger.warning(alert_msg)
    
    def save_csv(self, filename: Optional[str] = None):
        """
        Save readings to CSV file
        
        Args:
            filename: Output filename (auto-generated if None)
        """
        if not self.readings:
            logger.warning("No readings to save")
            return
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"bms_readings_{timestamp}.csv"
        
        filepath = self.output_dir / filename
        
        try:
            with open(filepath, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=['timestamp', 'device_id', 'sensor_name', 'value', 'unit'])
                writer.writeheader()
                
                for reading in self.readings:
                    writer.writerow(reading.to_dict())
            
            logger.info(f"Saved {len(self.readings)} readings to {filepath}")
        
        except Exception as e:
            logger.error(f"Error saving CSV: {e}")
    
    def save_json(self, filename: Optional[str] = None):
        """
        Save readings to JSON file
        
        Args:
            filename: Output filename (auto-generated if None)
        """
        if not self.readings:
            logger.warning("No readings to save")
            return
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"bms_readings_{timestamp}.json"
        
        filepath = self.output_dir / filename
        
        try:
            data = {
                'metadata': {
                    'timestamp': datetime.now().isoformat(),
                    'total_readings': len(self.readings),
                    'devices': list(self.devices.keys())
                },
                'readings': [r.to_dict() for r in self.readings]
            }
            
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"Saved {len(self.readings)} readings to {filepath}")
        
        except Exception as e:
            logger.error(f"Error saving JSON: {e}")
    
    def get_statistics(self, device_id: Optional[str] = None) -> Dict:
        """
        Calculate statistics for readings
        
        Args:
            device_id: Specific device (None = all devices)
            
        Returns:
            Dictionary of statistics
        """
        filtered = self.readings
        
        if device_id:
            filtered = [r for r in filtered if r.device_id == device_id]
        
        if not filtered:
            return {}
        
        # Group by sensor
        by_sensor = {}
        for reading in filtered:
            if reading.sensor_name not in by_sensor:
                by_sensor[reading.sensor_name] = []
            by_sensor[reading.sensor_name].append(reading.value)
        
        # Calculate statistics
        stats = {}
        for sensor_name, values in by_sensor.items():
            if values:
                stats[sensor_name] = {
                    'count': len(values),
                    'min': min(values),
                    'max': max(values),
                    'avg': sum(values) / len(values),
                    'latest': values[-1]
                }
        
        return stats
    
    def print_report(self):
        """Print a summary report"""
        print("\n" + "="*70)
        print("BMS MONITORING REPORT")
        print("="*70 + "\n")
        
        print(f"Total Readings: {len(self.readings)}")
        print(f"Devices Monitored: {len(self.devices)}\n")
        
        # Print per-device statistics
        for device_id in self.devices.keys():
            print(f"Device: {device_id}")
            stats = self.get_statistics(device_id)
            
            for sensor_name, sensor_stats in stats.items():
                print(f"  {sensor_name}:")
                print(f"    Latest: {sensor_stats['latest']:.2f}")
                print(f"    Min:    {sensor_stats['min']:.2f}")
                print(f"    Max:    {sensor_stats['max']:.2f}")
                print(f"    Avg:    {sensor_stats['avg']:.2f}")
            print()


def demo_monitoring():
    """Demonstrate monitoring system"""
    print("\n" + "="*70)
    print("BMS MONITORING SYSTEM DEMO")
    print("="*70 + "\n")
    
    # Create devices
    devices = [
        BMSDevice(device_id="OFFICE-A", location="Building A - Office"),
        BMSDevice(device_id="SERVER-B", location="Building B - Server Room"),
    ]
    
    # Start simulations
    for device in devices:
        device.start_simulation(update_interval=0.5)
    
    # Create monitor
    monitor = BMSMonitor(output_dir="./bms_logs")
    
    # Add devices to monitor
    for device in devices:
        monitor.add_device(device)
    
    # Run monitoring for 30 seconds
    print("Running monitoring for 30 seconds...\n")
    monitor.start_monitoring(interval=2.0, duration=30.0)
    
    # Save results
    print("\nSaving results...")
    monitor.save_csv()
    monitor.save_json()
    
    # Print report
    monitor.print_report()
    
    # Cleanup
    for device in devices:
        device.stop_simulation()
    
    print("Demo completed\n")


if __name__ == "__main__":
    try:
        demo_monitoring()
    except KeyboardInterrupt:
        print("\nDemo interrupted by user")
    except Exception as e:
        logger.exception("Demo error")
