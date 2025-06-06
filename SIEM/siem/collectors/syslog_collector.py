"""
Syslog Collector Module
Receives syslog messages via UDP and forwards them to the processor
"""

import socket
import threading
import queue
import json
from datetime import datetime
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.logger import setup_logger

class SyslogCollector:
    """Collects syslog messages from network devices"""
    
    def __init__(self, config, message_queue):
        """
        Initialize the syslog collector
        
        Args:
            config: Configuration dictionary
            message_queue: Queue to send messages to processor
        """
        self.config = config
        self.message_queue = message_queue
        self.logger = setup_logger(__name__)
        self.running = False
        self.socket = None
        
    def start(self):
        """Start the syslog collector"""
        try:
            # Create UDP socket
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
            # Bind to configured address and port
            bind_address = (
                self.config['syslog']['host'],
                self.config['syslog']['port']
            )
            self.socket.bind(bind_address)
            
            self.running = True
            self.logger.info(f"Syslog collector started on {bind_address[0]}:{bind_address[1]}")
            
            # Start collection loop
            self._collect_messages()
            
        except Exception as e:
            self.logger.error(f"Failed to start syslog collector: {e}")
            raise
            
    def stop(self):
        """Stop the syslog collector"""
        self.running = False
        if self.socket:
            self.socket.close()
        self.logger.info("Syslog collector stopped")
        
    def _collect_messages(self):
        """Main collection loop"""
        buffer_size = self.config['syslog']['buffer_size']
        
        while self.running:
            try:
                # Receive data
                data, addr = self.socket.recvfrom(buffer_size)
                
                if not data:
                    continue
                    
                # Decode and process message
                try:
                    decoded_data = data.decode(
                        self.config['syslog'].get('encoding', 'utf-8'),
                        errors='ignore'
                    )
                    
                    # Split multiple messages if present
                    for line in decoded_data.splitlines():
                        if line.strip():
                            # Create message object
                            message = {
                                'raw_message': line,
                                'source_ip': addr[0],
                                'source_port': addr[1],
                                'received_at': datetime.utcnow().isoformat(),
                                'collector_type': 'syslog'
                            }
                            
                            # Send to processor via queue
                            self.message_queue.put(message)
                            self.logger.debug(f"Received message from {addr[0]}:{addr[1]}")
                            
                except UnicodeDecodeError as e:
                    self.logger.warning(f"Failed to decode message from {addr}: {e}")
                    
            except socket.timeout:
                # Timeout is normal, just continue
                continue
                
            except Exception as e:
                if self.running:
                    self.logger.error(f"Error in collection loop: {e}")
                    
def create_collector(config, message_queue):
    """Factory function to create a syslog collector"""
    return SyslogCollector(config, message_queue) 