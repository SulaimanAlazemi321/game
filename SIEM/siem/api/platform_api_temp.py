"""
Platform API Module
Provides REST API endpoints for frontend interaction
"""

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from datetime import datetime, timedelta
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.logger import setup_logger
from indexer.models import LogEntry, Alert

class PlatformAPI:
    """REST API for SIEM platform management"""
    
    def __init__(self, config, db_manager):
        """
        Initialize the API
        
        Args:
            config: Configuration dictionary
            db_manager: Database manager instance
        """
        self.config = config
        self.db_manager = db_manager
        self.logger = setup_logger(__name__)
        
        # Create Flask app
        self.app = Flask(__name__)
        CORS(self.app)  # Enable CORS for frontend
        
        # Register routes
        self._register_routes()
        
    def _register_routes(self):
        """Register API routes"""
        
        @self.app.route('/api/health', methods=['GET'])
        def health():
            """Health check endpoint"""
            return jsonify({
                'status': 'healthy',
                'timestamp': datetime.utcnow().isoformat()
            })
            
        @self.app.route('/api/logs', methods=['GET'])
        def get_logs():
            """Get recent log entries"""
            try:
                # Get query parameters
                limit = int(request.args.get('limit', 100))
                offset = int(request.args.get('offset', 0))
                severity = request.args.get('severity')
                source_ip = request.args.get('source_ip')
                start_date = request.args.get('start_date')
                end_date = request.args.get('end_date')
                
                with self.db_manager.get_db_session() as session:
                    query = session.query(LogEntry)
                    
                    # Apply filters
                    if severity:
                        query = query.filter(LogEntry.severity == int(severity))
                    if source_ip:
                        query = query.filter(LogEntry.source_ip == source_ip)
                    if start_date:
                        start = datetime.fromisoformat(start_date)
                        query = query.filter(LogEntry.received_at >= start)
                    if end_date:
                        end = datetime.fromisoformat(end_date)
                        query = query.filter(LogEntry.received_at <= end)
                        
                    # Get total count
                    total = query.count()
                    
                    # Apply pagination
                    logs = query.order_by(LogEntry.received_at.desc())\
                               .offset(offset)\
                               .limit(limit)\
                               .all()
                               
                    return jsonify({
                        'logs': [log.to_dict() for log in logs],
                        'total': total,
                        'limit': limit,
                        'offset': offset
                    })
                    
            except Exception as e:
                self.logger.error(f"Error fetching logs: {e}")
                return jsonify({'error': str(e)}), 500
                
        @self.app.route('/api/alerts', methods=['GET'])
        def get_alerts():
            """Get security alerts"""
            try:
                # Get query parameters
                limit = int(request.args.get('limit', 50))
                offset = int(request.args.get('offset', 0))
                acknowledged = request.args.get('acknowledged')
                severity = request.args.get('severity')
                
                with self.db_manager.get_db_session() as session:
                    query = session.query(Alert)
                    
                    # Apply filters
                    if acknowledged is not None:
                        ack_value = 1 if acknowledged.lower() == 'true' else 0
                        query = query.filter(Alert.acknowledged == ack_value)
                    if severity:
                        query = query.filter(Alert.severity == severity)
                        
                    # Get total count
                    total = query.count()
                    
                    # Apply pagination
                    alerts = query.order_by(Alert.created_at.desc())\
                                 .offset(offset)\
                                 .limit(limit)\
                                 .all()
                                 
                    return jsonify({
                        'alerts': [alert.to_dict() for alert in alerts],
                        'total': total,
                        'limit': limit,
                        'offset': offset
                    })
                    
            except Exception as e:
                self.logger.error(f"Error fetching alerts: {e}")
                return jsonify({'error': str(e)}), 500
                
        @self.app.route('/api/alerts/<int:alert_id>/acknowledge', methods=['POST'])
        def acknowledge_alert(alert_id):
            """Acknowledge an alert"""
            try:
                data = request.get_json()
                acknowledged_by = data.get('acknowledged_by', 'system')
                
                with self.db_manager.get_db_session() as session:
                    alert = session.query(Alert).filter(Alert.id == alert_id).first()
                    
                    if not alert:
                        return jsonify({'error': 'Alert not found'}), 404
                        
                    alert.acknowledged = 1
                    alert.acknowledged_by = acknowledged_by
                    alert.acknowledged_at = datetime.utcnow()
                    
                    session.commit()
                    
                    return jsonify({
                        'message': 'Alert acknowledged',
                        'alert': alert.to_dict()
                    })
                    
            except Exception as e:
                self.logger.error(f"Error acknowledging alert: {e}")
                return jsonify({'error': str(e)}), 500
                
        @self.app.route('/api/stats/overview', methods=['GET'])
        def get_overview_stats():
            """Get system overview statistics"""
            try:
                with self.db_manager.get_db_session() as session:
                    # Get time range
                    now = datetime.utcnow()
                    last_24h = now - timedelta(hours=24)
                    last_7d = now - timedelta(days=7)
                    
                    # Total logs
                    total_logs = session.query(LogEntry).count()
                    logs_24h = session.query(LogEntry)\
                                     .filter(LogEntry.received_at >= last_24h)\
                                     .count()
                                     
                    # Total alerts
                    total_alerts = session.query(Alert).count()
                    alerts_24h = session.query(Alert)\
                                      .filter(Alert.created_at >= last_24h)\
                                      .count()
                                      
                    # Unacknowledged alerts
                    unack_alerts = session.query(Alert)\
                                         .filter(Alert.acknowledged == 0)\
                                         .count()
                                         
                    # Severity distribution
                    severity_dist = {}
                    for i in range(8):
                        count = session.query(LogEntry)\
                                      .filter(LogEntry.severity == i)\
                                      .filter(LogEntry.received_at >= last_24h)\
                                      .count()
                        severity_dist[i] = count
                        
                    return jsonify({
                        'total_logs': total_logs,
                        'logs_24h': logs_24h,
                        'total_alerts': total_alerts,
                        'alerts_24h': alerts_24h,
                        'unacknowledged_alerts': unack_alerts,
                        'severity_distribution': severity_dist,
                        'timestamp': now.isoformat()
                    })
                    
            except Exception as e:
                self.logger.error(f"Error fetching stats: {e}")
                return jsonify({'error': str(e)}), 500
                
        @self.app.route('/api/search', methods=['POST'])
        def search_logs():
            """Search logs with advanced filtering"""
            try:
                data = request.get_json()
                search_query = data.get('query', '')
                limit = int(data.get('limit', 100))
                
                with self.db_manager.get_db_session() as session:
                    query = session.query(LogEntry)
                    
                    # Search in message and raw_message
                    if search_query:
                        query = query.filter(
                            (LogEntry.message.contains(search_query)) |
                            (LogEntry.raw_message.contains(search_query))
                        )
                        
                    # Get results
                    results = query.order_by(LogEntry.received_at.desc())\
                                  .limit(limit)\
                                  .all()
                                  
                    return jsonify({
                        'results': [log.to_dict() for log in results],
                        'count': len(results),
                        'query': search_query
                    })
                    
            except Exception as e:
                self.logger.error(f"Error searching logs: {e}")
                return jsonify({'error': str(e)}), 500
                
    def start(self):
        """Start the API server"""
        host = self.config['api']['host']
        port = self.config['api']['port']
        debug = self.config['api'].get('debug', False)
        
        self.logger.info(f"Starting API server on {host}:{port}")
        self.app.run(host=host, port=port, debug=debug, use_reloader=False)
        
def create_api(config, db_manager):
    """Factory function to create API instance"""
    return PlatformAPI(config, db_manager) 
