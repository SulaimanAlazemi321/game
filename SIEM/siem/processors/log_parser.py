"""
Log Parser Module
Processes raw syslog messages using regex patterns
"""

import re
import threading
import queue
from datetime import datetime
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.logger import setup_logger

class LogParser:
    """Parses syslog messages using regex patterns"""
    
    # Common syslog patterns
    PATTERNS = {
        'standard': re.compile(
            r'^<(?P<priority>\d+)>'
            r'(?P<timestamp>[A-Za-z]{3}\s+\d+\s+\d{2}:\d{2}:\d{2})\s+'
            r'(?P<hostname>\S+)\s+'
            r'(?P<process>[^\[]+)\[(?P<pid>\d+)\]:\s'
            r'(?P<message>.+)$'
        ),
        'rfc3164': re.compile(
            r'^<(?P<priority>\d+)>'
            r'(?P<timestamp>\w{3}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2})\s+'
            r'(?P<hostname>[^\s]+)\s+'
            r'(?P<tag>[^:\s]+):\s*'
            r'(?P<message>.*)$'
        ),
        'rfc5424': re.compile(
            r'^<(?P<priority>\d+)>'
            r'(?P<version>\d+)\s+'
            r'(?P<timestamp>\S+)\s+'
            r'(?P<hostname>\S+)\s+'
            r'(?P<appname>\S+)\s+'
            r'(?P<procid>\S+)\s+'
            r'(?P<msgid>\S+)\s+'
            r'(?P<structured_data>\S+)\s*'
            r'(?P<message>.*)$'
        )
    }
    
    def __init__(self, config, input_queue, output_queue):
        """
        Initialize the log parser
        
        Args:
            config: Configuration dictionary
            input_queue: Queue to receive raw messages from collector
            output_queue: Queue to send parsed messages to indexer
        """
        self.config = config
        self.input_queue = input_queue
        self.output_queue = output_queue
        self.logger = setup_logger(__name__)
        self.running = False
        self.worker_thread = None
        
    def start(self):
        """Start the parser worker thread"""
        self.running = True
        self.worker_thread = threading.Thread(target=self._process_messages)
        self.worker_thread.daemon = True
        self.worker_thread.start()
        self.logger.info("Log parser started")
        
    def stop(self):
        """Stop the parser"""
        self.running = False
        if self.worker_thread:
            self.worker_thread.join(timeout=5)
        self.logger.info("Log parser stopped")
        
    def _process_messages(self):
        """Main processing loop"""
        while self.running:
            try:
                # Get message from queue with timeout
                message = self.input_queue.get(timeout=1)
                
                # Parse the message
                parsed = self._parse_message(message)
                
                if parsed:
                    # Send to indexer
                    self.output_queue.put(parsed)
                    self.logger.debug(f"Successfully parsed message from {message['source_ip']}")
                else:
                    self.logger.warning(f"Failed to parse message: {message['raw_message'][:100]}...")
                    
            except queue.Empty:
                # Timeout is normal, continue
                continue
                
            except Exception as e:
                self.logger.error(f"Error processing message: {e}")
                
    def _parse_message(self, message):
        """
        Parse a single message using regex patterns
        
        Args:
            message: Raw message dictionary from collector
            
        Returns:
            Parsed message dictionary or None if parsing fails
        """
        raw_msg = message['raw_message']
        
        # Try each pattern
        for pattern_name, pattern in self.PATTERNS.items():
            match = pattern.match(raw_msg)
            if match:
                parsed = match.groupdict()
                
                # Calculate facility and severity from priority
                if 'priority' in parsed:
                    priority = int(parsed['priority'])
                    parsed['facility'] = priority >> 3
                    parsed['severity'] = priority & 0x07
                    parsed['severity_name'] = self._get_severity_name(parsed['severity'])
                    
                # Add metadata
                parsed['pattern_matched'] = pattern_name
                parsed['source_ip'] = message['source_ip']
                parsed['source_port'] = message['source_port']
                parsed['received_at'] = message['received_at']
                parsed['parsed_at'] = datetime.utcnow().isoformat()
                parsed['raw_message'] = raw_msg
                
                return parsed
                
        # If no pattern matched, return basic parsed data
        return {
            'raw_message': raw_msg,
            'source_ip': message['source_ip'],
            'source_port': message['source_port'],
            'received_at': message['received_at'],
            'parsed_at': datetime.utcnow().isoformat(),
            'pattern_matched': 'none',
            'message': raw_msg
        }
        
    def _get_severity_name(self, severity):
        """Convert numeric severity to name"""
        severity_names = {
            0: 'Emergency',
            1: 'Alert',
            2: 'Critical',
            3: 'Error',
            4: 'Warning',
            5: 'Notice',
            6: 'Informational',
            7: 'Debug'
        }
        return severity_names.get(severity, 'Unknown')
        
def create_parser(config, input_queue, output_queue):
    """Factory function to create a log parser"""
    return LogParser(config, input_queue, output_queue) 