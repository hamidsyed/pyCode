"""
Client for Building Management System
Reads sensor data from BMS server
"""

import logging
import json
import socket
import time
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class BMSClient:
    """
    Client for reading data from BMS server
    """
    
    def __init__(self, host: str = "127.0.0.1", port: int = 47808,
                 timeout: float = 5.0):
        """
        Initialize Client
        
        Args:
            host: Server host address
            port: Server port number
            timeout: Socket timeout in seconds
        """
        self.host = host
        self.port = port
        self.timeout = timeout
        self.socket = None
        self.connected = False
        
        logger.info(f"Client initialized for {host}:{port}")
    
    def connect(self) -> bool:
        """
        Connect to BMS server
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(self.timeout)
            self.socket.connect((self.host, self.port))
            self.connected = True
            logger.info(f"Connected to {self.host}:{self.port}")
            return True
        except Exception as e:
            logger.error(f"Connection failed: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from server"""
        if self.socket:
            try:
                self.socket.close()
            except Exception as e:
                logger.error(f"Error closing socket: {e}")
        self.connected = False
        logger.info("Disconnected from server")
    
    def _send_request(self, request: Dict) -> Optional[Dict]:
        """
        Send request to server and get response
        
        Args:
            request: Request dictionary
            
        Returns:
            Response dictionary or None if error
        """
        if not self.connected:
            if not self.connect():
                return None
        
        try:
            # Send request
            request_str = json.dumps(request)
            self.socket.send(request_str.encode('utf-8'))
            
            # Receive response
            response_str = self.socket.recv(4096).decode('utf-8')
            response = json.loads(response_str)
            
            return response
        
        except Exception as e:
            logger.error(f"Error in request-response: {e}")
            self.connected = False
            return None
    
    def read_sensor(self, sensor_name: str) -> Optional[float]:
        """
        Read a single sensor value
        
        Args:
            sensor_name: Name of the sensor
            
        Returns:
            Sensor value or None if error
        """
        request = {
            'command': 'read_sensor',
            'sensor': sensor_name
        }
        
        response = self._send_request(request)
        
        if response and response.get('status') == 'success':
            return response.get('value')
        
        return None
    
    def read_all_sensors(self) -> Optional[Dict[str, float]]:
        """
        Read all sensor values
        
        Returns:
            Dictionary of sensor values or None if error
        """
        request = {'command': 'read_all'}
        
        response = self._send_request(request)
        
        if response and response.get('status') == 'success':
            return response.get('data')
        
        return None
    
    def get_device_info(self) -> Optional[Dict]:
        """
        Get device information
        
        Returns:
            Device info dictionary or None if error
        """
        request = {'command': 'device_info'}
        
        response = self._send_request(request)
        
        if response and response.get('status') == 'success':
            return response.get('info')
        
        return None
    
    def __enter__(self):
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()
    
    def __repr__(self) -> str:
        return f"BMSClient({self.host}:{self.port})"


# Backward compatibility aliases
BMSBACnetClient = BMSClient
SimpleBACnetClient = BMSClient


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Example usage
    client = BMSClient(host="127.0.0.1", port=47808)
    
    # Connect and read data
    if client.connect():
        # Get device info
        info = client.get_device_info()
        if info:
            print(f"Device Info: {info}\n")
        
        # Read all sensors
        data = client.read_all_sensors()
        if data:
            print("Sensor Values:")
            for sensor, value in data.items():
                print(f"  {sensor}: {value}")
        
        client.disconnect()
    else:
        logger.error("Failed to connect to server")
