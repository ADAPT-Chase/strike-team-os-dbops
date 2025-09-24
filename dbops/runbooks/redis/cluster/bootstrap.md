# Redis Cluster Bootstrap Runbook

## Overview
This runbook covers the bootstrap process for a 3-node Redis Cluster.

## Prerequisites
- Ubuntu 20.04+ or 22.04+
- Sufficient RAM (minimum 8GB recommended)
- Network ports 18010, 18011, 18012 open
- SystemD service files in place

## Bootstrap Process

### 1. System Preparation
```bash
# Create directories
sudo mkdir -p /data/databases/data/redis/{1,2,3}
sudo chown -R x:x /data/databases/data/redis

# Create log directory
sudo mkdir -p /var/log/redis
sudo chown -R x:x /var/log/redis
```

### 2. Configuration Setup
```bash
# Copy base configuration
cp /data/databases/dbops/configs/redis/cluster/base/redis.conf /data/databases/data/redis/1/redis-1.conf
cp /data/databases/dbops/configs/redis/cluster/base/redis.conf /data/databases/data/redis/2/redis-2.conf
cp /data/databases/dbops/configs/redis/cluster/base/redis.conf /data/databases/data/redis/3/redis-3.conf

# Update port configurations
sed -i 's/port 18010/port 18010/g' /data/databases/data/redis/1/redis-1.conf
sed -i 's/port 18010/port 18011/g' /data/databases/data/redis/2/redis-2.conf
sed -i 's/port 18010/port 18012/g' /data/databases/data/redis/3/redis-3.conf
```

### 3. SystemD Service Setup
```bash
# Copy and enable services
sudo cp /data/databases/dbops/infra/systemd/redis-cluster@.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable redis-cluster@{1,2,3}
```

### 4. Start Services
```bash
# Start individual nodes
sudo systemctl start redis-cluster@1
sudo systemctl start redis-cluster@2
sudo systemctl start redis-cluster@3

# Verify nodes are running
sudo systemctl status redis-cluster@{1,2,3}
```

### 5. Cluster Formation
```bash
# Create cluster (execute once)
redis-cli --cluster create \
  127.0.0.1:18010 \
  127.0.0.1:18011 \
  127.0.0.1:18012 \
  --cluster-replicas 0 \
  -a torrent_cluster_auth

# Verify cluster status
redis-cli -h 127.0.0.1 -p 18010 -a torrent_cluster_auth cluster nodes
```

## Validation
```bash
# Check cluster health
/data/databases/dbops/scripts/dbops health

# Check cluster info
redis-cli -h 127.0.0.1 -p 18010 -a torrent_cluster_auth cluster info

# Test connectivity to all nodes
redis-cli -h 127.0.0.1 -p 18010 -a torrent_cluster_auth ping
redis-cli -h 127.0.0.1 -p 18011 -a torrent_cluster_auth ping
redis-cli -h 127.0.0.1 -p 18012 -a torrent_cluster_auth ping
```

## Troubleshooting

### Common Issues

**Cluster not forming:**
- Check network connectivity between nodes
- Verify port accessibility
- Check Redis logs: `journalctl -u redis-cluster@1`

**Node not joining cluster:**
- Verify authentication password
- Check cluster configuration
- Reset cluster state: `redis-cli --cluster fix 127.0.0.1:18010`

**Memory issues:**
- Adjust maxmemory settings in configuration
- Monitor memory usage: `redis-cli info memory`

## Rollback
```bash
# Stop all services
sudo systemctl stop redis-cluster@{1,2,3}

# Remove cluster configuration
rm -f /data/databases/data/redis/*/nodes.conf

# Clear cluster state
redis-cli -h 127.0.0.1 -p 18010 -a torrent_cluster_auth cluster reset

# Restart services
sudo systemctl start redis-cluster@{1,2,3}
```

## Monitoring
- Monitor memory usage: `redis-cli info memory`
- Check cluster status: `redis-cli cluster info`
- Monitor key eviction: `redis-cli info stats | grep evicted`

## Security Notes
- Never expose Redis to public internet
- Use strong passwords
- Regularly rotate authentication credentials
- Monitor for unauthorized access attempts

---
**Runbook Version**: 1.0
**Last Updated**: 2025-09-23
**Owner**: DBOps Team