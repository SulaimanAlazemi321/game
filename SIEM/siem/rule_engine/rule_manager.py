"""
Rule Engine Module
Matches log entries against security rules and generates alerts
"""

import re
import threading
import queue
import yaml
import os
from datetime import datetime, timedelta
from collections import defaultdict, deque
import sys  
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.logger import setup_logger

class RuleManager:
    """Manages security rules and pattern matching"""
    
    def __init__(self, config, input_queue, db_manager):
        """
        Initialize the rule manager
        
        Args:
            config: Configuration dictionary
            input_queue: Queue to receive indexed logs
            db_manager: Database manager for saving alerts
        """
        self.config = config
        self.input_queue = input_queue
        self.db_manager = db_manager
        self.logger = setup_logger(__name__)
        self.running = False
        self.worker_thread = None
        
        # Rule storage
        self.rules = {}
        self.compiled_patterns = {}
        
        # Event tracking for threshold-based rules
        self.event_tracker = defaultdict(lambda: deque(maxlen=1000))
        
        # Load rules
        self._load_rules()
        
    def _load_rules(self):
        """Load rules from configuration directory"""
        rules_dir = self.config['rule_engine']['rules_directory']
        
        # Find all YAML rule files
        for filename in os.listdir(rules_dir):
            if filename.endswith('.yaml') or filename.endswith('.yml'):
                filepath = os.path.join(rules_dir, filename)
                self._load_rule_file(filepath)
                
        self.logger.info(f"Loaded {len(self.rules)} rules")
        
    def _load_rule_file(self, filepath):
        """Load rules from a single file"""
        try:
            with open(filepath, 'r') as f:
                data = yaml.safe_load(f)
                
            if 'rules' in data:
                for rule in data['rules']:
                    rule_id = rule['id']
                    self.rules[rule_id] = rule
                    
                    # Compile regex patterns
                    conditions = rule.get('conditions', {})
                    if 'message_pattern' in conditions:
                        pattern = conditions['message_pattern']
                        self.compiled_patterns[f"{rule_id}_message"] = re.compile(pattern, re.IGNORECASE)
                        
                    if 'process_pattern' in conditions:
                        pattern = conditions['process_pattern']
                        self.compiled_patterns[f"{rule_id}_process"] = re.compile(pattern, re.IGNORECASE)
                        
                    self.logger.debug(f"Loaded rule: {rule['name']}")
                    
        except Exception as e:
            self.logger.error(f"Error loading rule file {filepath}: {e}")
            
    def start(self):
        """Start the rule engine worker thread"""
        self.running = True
        self.worker_thread = threading.Thread(target=self._process_logs)
        self.worker_thread.daemon = True
        self.worker_thread.start()
        self.logger.info("Rule engine started")
        
    def stop(self):
        """Stop the rule engine"""
        self.running = False
        if self.worker_thread:
            self.worker_thread.join(timeout=5)
        self.logger.info("Rule engine stopped")
        
    def _process_logs(self):
        """Main processing loop"""
        while self.running:
            try:
                # Get log entry from queue
                log_entry = self.input_queue.get(timeout=1)
                
                # Check against all rules
                for rule_id, rule in self.rules.items():
                    if self._check_rule(rule_id, rule, log_entry):
                        self._generate_alert(rule, log_entry)
                        
            except queue.Empty:
                continue
                
            except Exception as e:
                self.logger.error(f"Error processing log: {e}")
                
    def _check_rule(self, rule_id, rule, log_entry):
        """
        Check if a log entry matches a rule
        
        Args:
            rule_id: Rule identifier
            rule: Rule dictionary
            log_entry: Log entry to check
            
        Returns:
            True if rule matches, False otherwise
        """
        conditions = rule.get('conditions', {})
        
        # Check message pattern
        if 'message_pattern' in conditions:
            pattern_key = f"{rule_id}_message"
            if pattern_key in self.compiled_patterns:
                message = log_entry.get('message', '') or log_entry.get('raw_message', '')
                if not self.compiled_patterns[pattern_key].search(message):
                    return False
                    
        # Check process pattern
        if 'process_pattern' in conditions:
            pattern_key = f"{rule_id}_process"
            if pattern_key in self.compiled_patterns:
                process = log_entry.get('process', '') or ''
                if not self.compiled_patterns[pattern_key].search(process):
                    return False
                    
        # Check threshold-based rules
        if 'threshold' in conditions:
            return self._check_threshold_rule(rule_id, rule, log_entry)
            
        # All conditions passed
        return True
        
    def _check_threshold_rule(self, rule_id, rule, log_entry):
        """Check threshold-based rules"""
        conditions = rule.get('conditions', {})
        threshold = conditions.get('threshold', 1)
        time_window = conditions.get('time_window', 3600)  # Default 1 hour
        group_by = conditions.get('group_by', 'source_ip')
        
        # Get grouping key
        group_key = log_entry.get(group_by, 'unknown')
        tracker_key = f"{rule_id}_{group_key}"
        
        # Add event to tracker
        now = datetime.utcnow()
        self.event_tracker[tracker_key].append(now)
        
        # Count events within time window
        cutoff_time = now - timedelta(seconds=time_window)
        recent_events = [t for t in self.event_tracker[tracker_key] if t > cutoff_time]
        
        # Update tracker with only recent events
        self.event_tracker[tracker_key] = deque(recent_events, maxlen=1000)
        
        # Check if threshold exceeded
        if len(recent_events) >= threshold:
            # Clear tracker to avoid duplicate alerts
            self.event_tracker[tracker_key].clear()
            return True
            
        return False
        
    def _generate_alert(self, rule, log_entry):
        """Generate an alert for a matched rule"""
        try:
            alert_data = {
                'rule_id': rule['id'],
                'rule_name': rule['name'],
                'severity': rule.get('severity', 'medium'),
                'description': rule.get('description', ''),
                'log_entry_id': log_entry.get('db_id'),
                'source_ip': log_entry.get('source_ip'),
                'destination_ip': log_entry.get('destination_ip')
            }
            
            # Save alert to database
            alert_id = self.db_manager.save_alert(alert_data)
            
            if alert_id:
                self.logger.warning(
                    f"ALERT: {rule['name']} - {rule.get('description', '')} "
                    f"[Source: {log_entry.get('source_ip', 'unknown')}]"
                )
                
        except Exception as e:
            self.logger.error(f"Error generating alert: {e}")
            
def create_rule_manager(config, input_queue, db_manager):
    """Factory function to create a rule manager"""
    return RuleManager(config, input_queue, db_manager) 