# SIEM (Security Information and Event Management) System

A modular, scalable SIEM system built with Python that collects, processes, indexes, and analyzes security logs in real-time.

## Architecture

The system follows a pipeline architecture with the following components:

```
Syslog Data → Collector → Parser → Database Indexer → Rule Engine → API/Frontend
     ↓            ↓          ↓            ↓                ↓            ↓
  (UDP:514)    (Queue)   (Regex)    (SQLite DB)    (Pattern Match)  (REST API)
```

### Components

1. **Syslog Collector** (`collectors/syslog_collector.py`)
   - Listens on UDP port 514 for syslog messages
   - Receives logs from network devices (including Kali Linux)
   - Forwards raw messages to the parser via message queue

2. **Log Parser** (`processors/log_parser.py`)
   - Parses syslog messages using regex patterns
   - Supports multiple syslog formats (RFC3164, RFC5424)
   - Extracts structured data from raw logs

3. **Database Indexer** (`indexer/db_manager.py`)
   - Stores parsed logs in SQLite database
   - Provides efficient indexing for fast queries
   - Manages batch processing for performance

4. **Rule Engine** (`rule_engine/rule_manager.py`)
   - Matches logs against security rules
   - Detects security threats and anomalies
   - Generates alerts for suspicious activities

5. **Platform API** (`api/platform_api.py`)
   - REST API for frontend integration
   - Provides endpoints for logs, alerts, and statistics
   - Enables real-time monitoring and management

## Installation

1. Install Python 3.8 or higher

2. Install dependencies:
   ```bash
   cd siem
   pip install -r requirements.txt
   ```

## Configuration

Edit `config/config.yaml` to customize:
- Syslog collector settings (host, port)
- Database location
- API settings
- Logging configuration

## Usage

### Starting the SIEM

```bash
cd siem
python main.py
```

The system will start all components and display:
- Syslog collector listening on UDP 514
- REST API available at http://localhost:5000
- Real-time log processing and alerting

### Sending Logs from Kali

Configure Kali to send syslog to the SIEM:

```bash
# Edit rsyslog configuration
sudo nano /etc/rsyslog.conf

# Add this line (replace SIEM_IP with your SIEM server IP)
*.* @SIEM_IP:514

# Restart rsyslog
sudo systemctl restart rsyslog
```

### API Endpoints

- `GET /api/health` - System health check
- `GET /api/logs` - Retrieve log entries
- `GET /api/alerts` - Get security alerts
- `POST /api/alerts/{id}/acknowledge` - Acknowledge an alert
- `GET /api/stats/overview` - System statistics
- `POST /api/search` - Search logs

### Example API Usage

```bash
# Get recent logs
curl http://localhost:5000/api/logs?limit=10

# Get unacknowledged alerts
curl http://localhost:5000/api/alerts?acknowledged=false

# Search logs
curl -X POST http://localhost:5000/api/search \
  -H "Content-Type: application/json" \
  -d '{"query": "Failed password"}'
```

## Security Rules

Default rules detect:
- SSH brute force attempts
- Privilege escalation
- Port scanning
- Malware signatures
- Configuration changes
- Service failures

Add custom rules in `rule_engine/rules/` as YAML files.

## Monitoring

- Logs are written to `siem.log`
- Database stored in `siem_data.db`
- Real-time alerts displayed in console
- API provides comprehensive statistics

## Architecture Benefits

1. **Modular Design**: Each component can be scaled independently
2. **Queue-Based**: Prevents data loss during high load
3. **Extensible**: Easy to add new parsers, rules, or collectors
4. **RESTful API**: Simple integration with any frontend
5. **Real-Time Processing**: Immediate threat detection

## Production Considerations

For production deployment:
1. Use PostgreSQL instead of SQLite
2. Deploy API with Gunicorn
3. Add Redis for caching
4. Implement log rotation
5. Enable TLS for API
6. Add authentication/authorization

## Troubleshooting

- **Port 514 in use**: Run with sudo or change port in config
- **No logs received**: Check firewall rules and syslog configuration
- **High memory usage**: Adjust queue sizes in main.py
- **Slow queries**: Add database indexes or use PostgreSQL

## License

This SIEM system is provided as-is for educational and security monitoring purposes. 