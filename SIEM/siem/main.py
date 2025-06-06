#!/usr/bin/env python3
"""
SIEM Main Entry Point
Orchestrates all components of the SIEM system
"""

import signal
import sys
import threading
import queue
import yaml
import time
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

from collectors.syslog_collector import create_collector
from processors.log_parser import create_parser
from indexer.db_manager import create_db_manager
from rule_engine.rule_manager import create_rule_manager
from api.platform_api import create_api
from utils.logger import setup_logger

class SIEMOrchestrator:
    """Main orchestrator for SIEM components"""
    
    def __init__(self, config_path='config/config.yaml'):
        """Initialize the SIEM system"""
        self.logger = setup_logger(__name__)
        self.running = False
        
        # Load configuration
        self.config = self._load_config(config_path)
        
        # Create message queues
        self.collector_to_parser = queue.Queue(maxsize=10000)
        self.parser_to_indexer = queue.Queue(maxsize=10000)
        self.indexer_to_rules = queue.Queue(maxsize=10000)
        
        # Initialize components
        self.logger.info("Initializing SIEM components...")
        
        # Create components
        self.collector = create_collector(self.config, self.collector_to_parser)
        self.parser = create_parser(self.config, self.collector_to_parser, self.parser_to_indexer)
        self.db_manager = create_db_manager(self.config, self.parser_to_indexer, self.indexer_to_rules)
        self.rule_manager = create_rule_manager(self.config, self.indexer_to_rules, self.db_manager)
        self.api = create_api(self.config, self.db_manager)
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
    def _load_config(self, config_path):
        """Load configuration from YAML file"""
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            self.logger.info(f"Configuration loaded from {config_path}")
            return config
        except Exception as e:
            self.logger.error(f"Failed to load configuration: {e}")
            sys.exit(1)
            
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        self.logger.info(f"Received signal {signum}, shutting down...")
        self.stop()
        sys.exit(0)
        
    def start(self):
        """Start all SIEM components"""
        try:
            self.running = True
            
            # Start components in order
            self.logger.info("Starting SIEM components...")
            
            # Start database manager
            self.db_manager.start()
            time.sleep(1)  # Give DB time to initialize
            
            # Start rule engine
            self.rule_manager.start()
            
            # Start parser
            self.parser.start()
            
            # Start API in a separate thread
            api_thread = threading.Thread(target=self.api.start)
            api_thread.daemon = True
            api_thread.start()
            
            # Start collector (blocking - runs in main thread)
            self.logger.info("All components started. SIEM system is operational.")
            self.collector.start()
            
        except Exception as e:
            self.logger.error(f"Failed to start SIEM: {e}")
            self.stop()
            sys.exit(1)
            
    def stop(self):
        """Stop all SIEM components"""
        self.running = False
        
        self.logger.info("Stopping SIEM components...")
        
        # Stop components in reverse order
        try:
            self.collector.stop()
        except:
            pass
            
        try:
            self.parser.stop()
        except:
            pass
            
        try:
            self.rule_manager.stop()
        except:
            pass
            
        try:
            self.db_manager.stop()
        except:
            pass
            
        self.logger.info("SIEM system stopped.")

def main():
    """Main entry point"""
    print("""
    ╔═══════════════════════════════════════════╗
    ║          SIEM System Starting...          ║
    ║                                           ║
    ║  Components:                              ║
    ║  • Syslog Collector (UDP 514)            ║
    ║  • Log Parser (Regex Engine)             ║
    ║  • Database Indexer (SQLite)             ║
    ║  • Rule Engine (Pattern Matching)        ║
    ║  • REST API (Flask - Port 5000)          ║
    ╚═══════════════════════════════════════════╝
    """)
    
    # Create and start orchestrator
    orchestrator = SIEMOrchestrator()
    
    try:
        orchestrator.start()
    except KeyboardInterrupt:
        print("\nShutdown requested...")
        orchestrator.stop()
    except Exception as e:
        print(f"\nError: {e}")
        orchestrator.stop()
        sys.exit(1)

if __name__ == '__main__':
    main() 