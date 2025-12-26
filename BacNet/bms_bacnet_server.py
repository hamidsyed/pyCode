"""
Server for BMS Device
Exposes BMS sensor data via socket-based network protocol
"""

import logging
import json
import socket
import threading
import time
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class BMSServer:
    """
    Socket-based Server for Building Management System
    Exposes sensor data over network protocol
    """
    
    def __init__(self, bms_device, device_id: int = 12345, 
                 device_name: str = "BMS-Device", 
                 host: str = "127.0.0.1", port: int = 47808):
        """
        Initialize Server
        
        Args:
            bms_device: BMSDevice instance to expose
            device_id: Device identifier (integer)
            device_name: Name of the device
            host: Host IP address
            port: Server port number
        """
        self.bms_device = bms_device
        self.device_id = device_id
        self.device_name = device_name
        self.host = host
        self.port = port
        
        self.socket = None
        self.sensor_objects = {}
        self.running = False
        self.server_thread = None
        self.client_threads = []
        
        logger.info(f"Server initialized for {device_name} on {host}:{port}")
    
    def initialize(self):
        """Initialize server and sensor objects"""
        try:
            # Create sensor metadata cache
            sensor_data = self.bms_device.get_sensor_data()
            
            for sensor_name in sensor_data.keys():
                try:
                    metadata = self.bms_device.get_sensor_metadata(sensor_name)
                    self.sensor_objects[sensor_name] = metadata
                    logger.info(f"Created object for {sensor_name}")
                    
                except Exception as e:
                    logger.error(f"Failed to create object for {sensor_name}: {e}")
            
            logger.info("Server initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize server: {e}", exc_info=True)
            return False
    
    def start(self):
        """Start the server"""
        if self.running:
            logger.warning("Server already running")
            return
        
        if not self.sensor_objects:
            if not self.initialize():
                return
        
        self.running = True
        self.server_thread = threading.Thread(
            target=self._run_server,
            daemon=True
        )
        self.server_thread.start()
        logger.info(f"Server started on {self.host}:{self.port}")
    
    def stop(self):
        """Stop the server"""
        self.running = False
        if self.socket:
            try:
                self.socket.close()
            except Exception as e:
                logger.error(f"Error closing socket: {e}")
        
        # Wait for threads
        for thread in self.client_threads:
            thread.join(timeout=1)
        
        logger.info("Server stopped")
    
    def _run_server(self):
        """Run the server"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.bind((self.host, self.port))
            self.socket.listen(5)
            self.socket.settimeout(1.0)
            
            logger.info(f"Server listening on {self.host}:{self.port}")
            
            while self.running:
                try:
                    client_socket, client_addr = self.socket.accept()
                    client_thread = threading.Thread(
                        target=self._handle_client,
                        args=(client_socket, client_addr),
                        daemon=True
                    )
                    client_thread.start()
                    self.client_threads.append(client_thread)
                    logger.info(f"Client connected from {client_addr}")
                    
                except socket.timeout:
                    continue
                except Exception as e:
                    if self.running:
                        logger.error(f"Error accepting client: {e}")
        
        except Exception as e:
            logger.error(f"Error in server loop: {e}", exc_info=True)
        finally:
            self.running = False
    
    def _handle_client(self, client_socket: socket.socket, client_addr):
        """Handle client connection"""
        try:
            while self.running:
                data = client_socket.recv(1024).decode('utf-8')
                
                if not data:
                    break
                
                # Parse request
                response = self._process_request(data)
                
                # Send response
                client_socket.send(response.encode('utf-8'))
        
        except Exception as e:
            logger.error(f"Error handling client {client_addr}: {e}")
        finally:
            try:
                client_socket.close()
            except:
                pass
            logger.info(f"Client {client_addr} disconnected")
    
    def _process_request(self, request_str: str) -> str:
        """Process client request and return response"""
        try:
            request = json.loads(request_str)
            command = request.get('command')
            
            if command == 'read_sensor':
                sensor_name = request.get('sensor')
                value = self.get_sensor_value(sensor_name)
                response = {
                    'status': 'success',
                    'sensor': sensor_name,
                    'value': value
                }
            
            elif command == 'read_all':
                data = self.bms_device.get_sensor_data()
                # Convert to serializable format
                data_dict = {k: float(v) for k, v in data.items()}
                response = {
                    'status': 'success',
                    'data': data_dict,
                    'timestamp': time.time()
                }
            
            elif command == 'device_info':
                response = {
                    'status': 'success',
                    'info': self.get_device_info()
                }
            
            else:
                response = {'status': 'error', 'message': 'Unknown command'}
            
            return json.dumps(response)
        
        except Exception as e:
            logger.error(f"Error processing request: {e}")
            return json.dumps({'status': 'error', 'message': str(e)})
    
    def get_sensor_value(self, sensor_name: str) -> Optional[float]:
        """
        Get the current value of a sensor
        
        Args:
            sensor_name: Name of the sensor
            
        Returns:
            Current sensor value or None if not found
        """
        try:
            return float(self.bms_device.get_sensor_value(sensor_name))
        except Exception as e:
            logger.error(f"Error getting sensor value: {e}")
            return None
    
    def get_device_info(self) -> Dict:
        """Get device information"""
        return {
            'device_id': self.device_id,
            'device_name': self.device_name,
            'address': f"{self.host}:{self.port}",
            'running': self.running,
            'sensors': list(self.sensor_objects.keys())
        }
    
    def __repr__(self) -> str:
        return f"BMSServer({self.device_name}, {self.host}:{self.port})"


# Backward compatibility alias
BMSBACnetServer = BMSServer


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    from bms_simulator import BMSDevice
    
    # Create BMS device
    bms = BMSDevice(device_id="BMS-001", location="Test Location")
    bms.start_simulation(update_interval=1.0)
    
    # Create and start server
    server = BMSServer(
        bms,
        device_id=12345,
        device_name="BMS-Server-01",
        host="127.0.0.1",
        port=47808
    )
    
    if server.initialize():
        server.start()
        
        try:
            logger.info("Server running... Press Ctrl+C to stop")
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Shutting down...")
        finally:
            server.stop()
            bms.stop_simulation()
    else:
        logger.error("Failed to initialize server")
