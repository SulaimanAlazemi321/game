"""
Database Manager Module
Handles indexing of parsed logs into the database
"""

import threading
import queue
from datetime import datetime
from contextlib import contextmanager
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.logger import setup_logger
from indexer.models import init_database, get_session, LogEntry, Alert

class DatabaseManager:
    """Manages database operations for log indexing"""
    
    def __init__(self, config, input_queue, alert_queue=None):
        """
        Initialize the database manager
        
        Args:
            config: Configuration dictionary
            input_queue: Queue to receive parsed messages from parser
            alert_queue: Optional queue to send logs to rule engine
        """
        self.config = config
        self.input_queue = input_queue
        self.alert_queue = alert_queue
        self.logger = setup_logger(__name__)
        self.running = False
        self.worker_thread = None
        
        # Initialize database
        db_path = config['database']['path']
        self.engine = init_database(db_path)
        self.logger.info(f"Database initialized at {db_path}")
        
    @contextmanager
    def get_db_session(self):
        """Context manager for database sessions"""
        session = get_session(self.engine)
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
            
    def start(self):
        """Start the indexer worker thread"""
        self.running = True
        self.worker_thread = threading.Thread(target=self._index_messages)
        self.worker_thread.daemon = True
        self.worker_thread.start()
        self.logger.info("Database indexer started")
        
    def stop(self):
        """Stop the indexer"""
        self.running = False
        if self.worker_thread:
            self.worker_thread.join(timeout=5)
        self.logger.info("Database indexer stopped")
        
    def _index_messages(self):
        """Main indexing loop"""
        batch = []
        batch_size = 10  # Process in batches for efficiency
        
        while self.running:
            try:
                # Get message from queue with timeout
                message = self.input_queue.get(timeout=1)
                batch.append(message)
                
                # Process batch if it's full
                if len(batch) >= batch_size:
                    self._process_batch(batch)
                    batch = []
                    
            except queue.Empty:
                # Process any remaining messages in batch
                if batch:
                    self._process_batch(batch)
                    batch = []
                continue
                
            except Exception as e:
                self.logger.error(f"Error in indexing loop: {e}")
                
    def _process_batch(self, messages):
        """Process a batch of messages"""
        try:
            with self.get_db_session() as session:
                for message in messages:
                    # Create log entry
                    log_entry = self._create_log_entry(message)
                    session.add(log_entry)
                    
                # Commit the batch
                session.commit()
                
                # Send to rule engine if configured
                if self.alert_queue:
                    for message in messages:
                        # Add database ID to message
                        message['db_id'] = log_entry.id
                        self.alert_queue.put(message)
                        
                self.logger.debug(f"Indexed batch of {len(messages)} messages")
                
        except Exception as e:
            self.logger.error(f"Error processing batch: {e}")
            
    def _create_log_entry(self, message):
        """Create a LogEntry object from parsed message"""
        # Parse timestamps
        parsed_at = None
        if 'parsed_at' in message:
            try:
                parsed_at = datetime.fromisoformat(message['parsed_at'])
            except:
                pass
                
        received_at = None
        if 'received_at' in message:
            try:
                received_at = datetime.fromisoformat(message['received_at'])
            except:
                pass
        
        # Create log entry
        log_entry = LogEntry(
            raw_message=message.get('raw_message', ''),
            message=message.get('message', ''),
            source_ip=message.get('source_ip'),
            source_port=message.get('source_port'),
            hostname=message.get('hostname'),
            priority=message.get('priority'),
            facility=message.get('facility'),
            severity=message.get('severity'),
            severity_name=message.get('severity_name'),
            process=message.get('process'),
            pid=message.get('pid'),
            appname=message.get('appname'),
            timestamp=message.get('timestamp'),
            received_at=received_at,
            parsed_at=parsed_at,
            pattern_matched=message.get('pattern_matched')
        )
        
        return log_entry
        
    def save_alert(self, alert_data):
        """Save an alert to the database"""
        try:
            with self.get_db_session() as session:
                alert = Alert(
                    rule_id=alert_data['rule_id'],
                    rule_name=alert_data['rule_name'],
                    severity=alert_data['severity'],
                    description=alert_data['description'],
                    log_entry_id=alert_data.get('log_entry_id'),
                    source_ip=alert_data.get('source_ip'),
                    destination_ip=alert_data.get('destination_ip')
                )
                session.add(alert)
                session.commit()
                self.logger.info(f"Alert saved: {alert_data['rule_name']}")
                return alert.id
                
        except Exception as e:
            self.logger.error(f"Error saving alert: {e}")
            return None
            
def create_db_manager(config, input_queue, alert_queue=None):
    """Factory function to create a database manager"""
    return DatabaseManager(config, input_queue, alert_queue) 