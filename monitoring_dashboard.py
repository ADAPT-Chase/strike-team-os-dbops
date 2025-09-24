#!/usr/bin/env python3
"""
Strike Team OS - Comprehensive Service Monitoring Dashboard
Author: Vector - Systems Engineer & Database Architect
Date: September 24, 2025
Mission: Real-time monitoring dashboard for all 18xxx database services
"""

import json
import subprocess
import time
import socket
import requests
import threading
from datetime import datetime, timedelta
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import os

class ServiceMonitor:
    def __init__(self):
        self.service_ports = {
            'dragonfly': 18000,
            'redis': 18010,
            'postgresql': 18020,
            'timescaledb': 18020,
            'qdrant': 18003,
            'neo4j': 18040,
            'redpanda': 18090,
            'influxdb': 18200,
            'minio': 18170,
            'etcd': 18230,
            'ipfs': 18180,
            'janusgraph': 18220,
            'elasticsearch': 18991,
            'chromadb': 18270,
            'faiss': 18271,
            'haystack': 18240,
            'weaviate': 18110
        }

        self.service_status = {}
        self.service_history = {}
        self.monitoring_interval = 30  # seconds
        self.last_update = datetime.now()

    def check_port_connectivity(self, host, port, timeout=5):
        """Check if a port is accessible"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(timeout)
                result = s.connect_ex((host, port))
                return result == 0
        except:
            return False

    def check_service_health(self, service_name, port):
        """Check health of specific service"""
        try:
            if service_name == 'postgresql':
                # Check PostgreSQL with proper connection
                import psycopg2
                conn = psycopg2.connect(
                    host="localhost",
                    port=port,
                    database="postgres",
                    user="postgres"
                )
                conn.close()
                return {'status': 'healthy', 'details': 'Database connection successful'}

            elif service_name == 'redpanda':
                # Check Redpanda cluster health
                result = subprocess.run(
                    ['rpk', 'cluster', 'info', '--brokers', f'localhost:{port}'],
                    capture_output=True, text=True, timeout=10
                )
                if result.returncode == 0:
                    return {'status': 'healthy', 'details': 'Cluster accessible'}

            elif service_name == 'dragonfly':
                # Check DragonFly with Redis CLI
                result = subprocess.run(
                    ['redis-cli', '-p', str(port), 'PING'],
                    capture_output=True, text=True, timeout=5
                )
                if result.returncode == 0 and 'PONG' in result.stdout:
                    return {'status': 'healthy', 'details': 'Redis PING successful'}

            elif service_name in ['chromadb', 'faiss', 'haystack']:
                # Check HTTP-based services
                try:
                    response = requests.get(f'http://localhost:{port}/health', timeout=5)
                    if response.status_code == 200:
                        return {'status': 'healthy', 'details': 'HTTP health check passed'}
                except:
                    try:
                        response = requests.get(f'http://localhost:{port}/', timeout=5)
                        if response.status_code == 200:
                            return {'status': 'healthy', 'details': 'HTTP root accessible'}
                    except:
                        pass

            elif service_name == 'etcd':
                # Check etcd health
                result = subprocess.run(
                    ['etcdctl', 'endpoint', 'health', f'--endpoints=localhost:{port}'],
                    capture_output=True, text=True, timeout=5
                )
                if result.returncode == 0:
                    return {'status': 'healthy', 'details': 'etcd endpoint healthy'}

            # Default port connectivity check
            if self.check_port_connectivity('localhost', port):
                return {'status': 'accessible', 'details': 'Port is accessible'}

        except Exception as e:
            return {'status': 'error', 'details': str(e)}

        return {'status': 'unreachable', 'details': 'Port not accessible'}

    def update_service_status(self):
        """Update status for all services"""
        current_time = datetime.now()

        for service_name, port in self.service_ports.items():
            status = self.check_service_health(service_name, port)

            service_info = {
                'name': service_name,
                'port': port,
                'status': status['status'],
                'details': status['details'],
                'last_check': current_time.isoformat(),
                'uptime_percentage': self.calculate_uptime(service_name, status['status'])
            }

            self.service_status[service_name] = service_info

            # Update history
            if service_name not in self.service_history:
                self.service_history[service_name] = []

            self.service_history[service_name].append({
                'timestamp': current_time.isoformat(),
                'status': status['status']
            })

            # Keep only last 100 history entries
            if len(self.service_history[service_name]) > 100:
                self.service_history[service_name] = self.service_history[service_name][-100:]

        self.last_update = current_time

    def calculate_uptime(self, service_name, current_status):
        """Calculate uptime percentage based on history"""
        if service_name not in self.service_history:
            return 100.0 if current_status == 'healthy' else 0.0

        history = self.service_history[service_name]
        if len(history) < 2:
            return 100.0 if current_status == 'healthy' else 0.0

        healthy_count = sum(1 for entry in history if entry['status'] == 'healthy')
        return (healthy_count / len(history)) * 100

    def get_dashboard_data(self):
        """Get comprehensive dashboard data"""
        total_services = len(self.service_status)
        healthy_services = sum(1 for s in self.service_status.values() if s['status'] == 'healthy')
        accessible_services = sum(1 for s in self.service_status.values() if s['status'] in ['healthy', 'accessible'])

        return {
            'summary': {
                'total_services': total_services,
                'healthy_services': healthy_services,
                'accessible_services': accessible_services,
                'health_percentage': (healthy_services / total_services * 100) if total_services > 0 else 0,
                'accessibility_percentage': (accessible_services / total_services * 100) if total_services > 0 else 0,
                'last_update': self.last_update.isoformat()
            },
            'services': self.service_status,
            'port_standardization': {
                'compliant_services': len(self.service_status),
                'total_ports_assigned': len(self.service_ports),
                'standard': '18xxx port range',
                'documentation': '/data/databases/dbops/configs/ports.yaml'
            }
        }

    def start_monitoring(self):
        """Start continuous monitoring"""
        def monitor_loop():
            while True:
                try:
                    self.update_service_status()
                    time.sleep(self.monitoring_interval)
                except Exception as e:
                    print(f"Monitoring error: {e}")
                    time.sleep(5)

        monitoring_thread = threading.Thread(target=monitor_loop, daemon=True)
        monitoring_thread.start()

class DashboardHTTPHandler(BaseHTTPRequestHandler):
    def __init__(self, *args, monitor=None, **kwargs):
        self.monitor = monitor
        super().__init__(*args, **kwargs)

    def do_GET(self):
        """Handle GET requests"""
        try:
            parsed_path = urllib.parse.urlparse(self.path)
            path = parsed_path.path

            if path == '/' or path == '/dashboard':
                self.serve_dashboard()
            elif path == '/api/status':
                self.serve_api_status()
            elif path == '/api/services':
                self.serve_api_services()
            else:
                self.send_404()

        except Exception as e:
            self.send_error(500, str(e))

    def serve_dashboard(self):
        """Serve the main dashboard HTML"""
        html = """
<!DOCTYPE html>
<html>
<head>
    <title>Strike Team OS - Service Monitoring Dashboard</title>
    <meta charset="UTF-8">
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
        .header { background: #2c3e50; color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
        .summary { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-bottom: 20px; }
        .summary-card { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .summary-card h3 { margin: 0 0 10px 0; color: #2c3e50; }
        .summary-card .value { font-size: 24px; font-weight: bold; color: #3498db; }
        .services-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 15px; }
        .service-card { background: white; padding: 15px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .service-card.healthy { border-left: 4px solid #27ae60; }
        .service-card.accessible { border-left: 4px solid #f39c12; }
        .service-card.error { border-left: 4px solid #e74c3c; }
        .service-card.unreachable { border-left: 4px solid #95a5a6; }
        .service-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
        .service-name { font-weight: bold; color: #2c3e50; }
        .service-status { padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: bold; }
        .status-healthy { background: #d4edda; color: #155724; }
        .status-accessible { background: #fff3cd; color: #856404; }
        .status-error { background: #f8d7da; color: #721c24; }
        .status-unreachable { background: #e2e3e5; color: #383d41; }
        .service-details { font-size: 14px; color: #666; margin-bottom: 5px; }
        .service-meta { font-size: 12px; color: #999; }
        .refresh-info { text-align: center; margin-top: 20px; color: #666; }
    </style>
    <script>
        function updateDashboard() {
            fetch('/api/status')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('total-services').textContent = data.summary.total_services;
                    document.getElementById('healthy-services').textContent = data.summary.healthy_services;
                    document.getElementById('health-percentage').textContent = data.summary.health_percentage.toFixed(1) + '%';
                    document.getElementById('last-update').textContent = new Date(data.summary.last_update).toLocaleString();
                });

            fetch('/api/services')
                .then(response => response.json())
                .then(data => {
                    const servicesContainer = document.getElementById('services-container');
                    servicesContainer.innerHTML = '';

                    for (const [serviceName, serviceInfo] of Object.entries(data)) {
                        const serviceCard = document.createElement('div');
                        serviceCard.className = `service-card ${serviceInfo.status}`;

                        serviceCard.innerHTML = `
                            <div class="service-header">
                                <div class="service-name">${serviceName.toUpperCase()}</div>
                                <div class="service-status status-${serviceInfo.status}">${serviceInfo.status.toUpperCase()}</div>
                            </div>
                            <div class="service-details">${serviceInfo.details}</div>
                            <div class="service-meta">
                                Port: ${serviceInfo.port} |
                                Uptime: ${serviceInfo.uptime_percentage.toFixed(1)}% |
                                Last check: ${new Date(serviceInfo.last_check).toLocaleTimeString()}
                            </div>
                        `;

                        servicesContainer.appendChild(serviceCard);
                    }
                });
        }

        // Update dashboard every 30 seconds
        setInterval(updateDashboard, 30000);

        // Initial load
        updateDashboard();
    </script>
</head>
<body>
    <div class="header">
        <h1>Strike Team OS - Service Monitoring Dashboard</h1>
        <p>Real-time monitoring for all 18xxx database services</p>
    </div>

    <div class="summary">
        <div class="summary-card">
            <h3>Total Services</h3>
            <div class="value" id="total-services">-</div>
        </div>
        <div class="summary-card">
            <h3>Healthy Services</h3>
            <div class="value" id="healthy-services">-</div>
        </div>
        <div class="summary-card">
            <h3>Health Percentage</h3>
            <div class="value" id="health-percentage">-</div>
        </div>
        <div class="summary-card">
            <h3>Last Update</h3>
            <div class="value" id="last-update">-</div>
        </div>
    </div>

    <div class="services-grid" id="services-container">
        <!-- Services will be loaded here -->
    </div>

    <div class="refresh-info">
        Dashboard auto-refreshes every 30 seconds | Last update: <span id="current-time">-</span>
        <script>
            document.getElementById('current-time').textContent = new Date().toLocaleString();
            setInterval(() => {
                document.getElementById('current-time').textContent = new Date().toLocaleString();
            }, 1000);
        </script>
    </div>
</body>
</html>
        """

        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode())

    def serve_api_status(self):
        """Serve API status endpoint"""
        if self.monitor:
            data = self.monitor.get_dashboard_data()
            response = json.dumps(data, indent=2)
        else:
            response = json.dumps({'error': 'Monitor not available'})

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(response.encode())

    def serve_api_services(self):
        """Serve API services endpoint"""
        if self.monitor:
            response = json.dumps(self.monitor.service_status, indent=2)
        else:
            response = json.dumps({'error': 'Monitor not available'})

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(response.encode())

    def send_404(self):
        """Send 404 response"""
        self.send_response(404)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b'<h1>404 Not Found</h1>')

def run_dashboard_server(monitor, port=18999):
    """Run the dashboard HTTP server"""
    def handler(*args, **kwargs):
        return DashboardHTTPHandler(*args, monitor=monitor, **kwargs)

    server = HTTPServer(('0.0.0.0', port), handler)
    print(f"Dashboard server running on http://localhost:{port}")
    server.serve_forever()

def main():
    """Main function to start the monitoring dashboard"""
    print("Starting Strike Team OS Service Monitoring Dashboard...")

    # Initialize monitor
    monitor = ServiceMonitor()

    # Initial status update
    monitor.update_service_status()

    # Start background monitoring
    monitor.start_monitoring()

    # Start web server
    dashboard_port = 18999  # Use 18xxx port range
    print(f"Dashboard will be available at: http://localhost:{dashboard_port}")
    print("Starting monitoring services...")

    try:
        run_dashboard_server(monitor, dashboard_port)
    except KeyboardInterrupt:
        print("\nShutting down dashboard...")
    except Exception as e:
        print(f"Dashboard error: {e}")

if __name__ == "__main__":
    main()