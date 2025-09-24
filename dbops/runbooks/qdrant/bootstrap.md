# Qdrant Bootstrap Runbook

## Overview
This runbook covers the bootstrap process for Qdrant vector database.

## Prerequisites
- Ubuntu 20.04+ or 22.04+
- Sufficient RAM (minimum 4GB recommended)
- Network ports 18001 (HTTP) and 18002 (gRPC) open
- SystemD service files in place

## Bootstrap Process

### 1. System Preparation
```bash
# Create directories
sudo mkdir -p /data/databases/data/qdrant/{storage,snapshots}
sudo chown -R x:x /data/databases/data/qdrant

# Create log directory
sudo mkdir -p /var/log/qdrant
sudo chown -R x:x /var/log/qdrant
```

### 2. Qdrant Installation
```bash
# Download Qdrant binary
curl -L https://github.com/qdrant/qdrant/releases/download/v1.15.4/qdrant-x86_64-unknown-linux-gnu.tar.gz -o qdrant.tar.gz
tar -xzf qdrant.tar.gz
sudo mv qdrant /usr/local/bin/
sudo chmod +x /usr/local/bin/qdrant
```

### 3. Configuration Setup
```bash
# Copy configuration
sudo cp /data/databases/dbops/configs/qdrant/base/config.yaml /data/databases/qdrant/config.yaml
sudo chown x:x /data/databases/qdrant/config.yaml
```

### 4. SystemD Service Setup
```bash
# Copy and enable service
sudo cp /data/databases/dbops/infra/systemd/qdrant.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable qdrant
```

### 5. Start Service
```bash
# Start Qdrant
sudo systemctl start qdrant

# Verify service is running
sudo systemctl status qdrant
```

## Validation
```bash
# Check HTTP endpoint
curl -s http://localhost:18001/ | jq .

# Check gRPC endpoint (requires grpcurl)
grpcurl -plaintext localhost:18002 qdrant.Qdrant/HealthCheck

# Check service logs
journalctl -u qdrant -f

# Verify with dbops script
/data/databases/dbops/scripts/dbops health
```

## Collection Management

### Create Collection
```bash
curl -X PUT http://localhost:18001/collections/test_collection \
  -H "Content-Type: application/json" \
  -d '{
    "vectors": {
      "size": 768,
      "distance": "Cosine"
    }
  }'
```

### Check Collections
```bash
curl -s http://localhost:18001/collections | jq .
```

## Troubleshooting

### Common Issues

**Service not starting:**
- Check configuration file syntax
- Verify directory permissions
- Check port availability: `ss -tlnp | grep -E '18001|18002'`
- Review logs: `journalctl -u qdrant`

**Memory issues:**
- Adjust memory limits in SystemD service
- Monitor memory usage: `htop`
- Check Qdrant metrics: `curl -s http://localhost:18001/metrics`

**Storage issues:**
- Verify disk space: `df -h /data/databases/data/qdrant`
- Check storage path permissions
- Monitor storage usage in Qdrant metrics

### Performance Optimization

**Memory settings:**
- Adjust cache_size in configuration
- Monitor memory usage patterns
- Consider vector dimension impact

**Disk I/O:**
- Use SSD storage for better performance
- Monitor disk latency: `iostat -x 1`
- Adjust snapshot intervals

## Rollback
```bash
# Stop service
sudo systemctl stop qdrant

# Remove data directories
sudo rm -rf /data/databases/data/qdrant/storage/*
sudo rm -rf /data/databases/data/qdrant/snapshots/*

# Restart service
sudo systemctl start qdrant
```

## Monitoring

### Health Checks
```bash
# HTTP health check
curl -f http://localhost:18001/

# Detailed metrics
curl -s http://localhost:18001/metrics

# Collection statistics
curl -s http://localhost:18001/collections/<collection_name>/stats
```

### Key Metrics to Monitor
- Number of vectors
- Memory usage
- Disk usage
- Query latency
- Index performance

## Security Notes
- Enable authentication in production
- Use TLS for all communications
- Regularly update Qdrant version
- Monitor for unusual query patterns
- Implement rate limiting for public endpoints

## Backup Strategy
```bash
# Create snapshot
curl -X POST http://localhost:18001/snapshots \
  -H "Content-Type: application/json" \
  -d '{"name": "manual_backup_$(date +%Y%m%d_%H%M%S)"}'

# List snapshots
curl -s http://localhost:18001/snapshots | jq .

# Create collection snapshot
curl -X POST http://localhost:18001/collections/<collection_name>/snapshots \
  -H "Content-Type: application/json" \
  -d '{"name": "collection_backup_$(date +%Y%m%d_%H%M%S)"}'
```

---
**Runbook Version**: 1.0
**Last Updated**: 2025-09-23
**Owner**: DBOps Team