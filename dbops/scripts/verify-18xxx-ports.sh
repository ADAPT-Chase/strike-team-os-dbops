#!/bin/bash
# DBOps 18xxx Port Verification Script
# Verifies all services are listening on assigned 18xxx ports
# Author: Vector, Systems Engineer & Database Architect

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== DBOps 18xxx Port Verification ===${NC}"
echo "Checking all assigned 18xxx ports..."
echo

# Expected services and their ports
declare -A expected_services=(
    # Core Services
    ["18000"]="DragonFly Primary"
    ["18001"]="DragonFly Secondary"
    ["18003"]="Qdrant HTTP"
    ["18004"]="Qdrant gRPC"
    ["18010"]="Redis Cluster Node 1"
    ["18011"]="Redis Cluster Node 2"
    ["18012"]="Redis Cluster Node 3"
    ["18020"]="PostgreSQL"
    ["18040"]="Neo4j Bolt"
    ["18041"]="Neo4j HTTP"
    ["18042"]="Neo4j HTTPS"
    ["18080"]="Trino"
    ["18090"]="Redpanda Kafka"
    ["18091"]="Redpanda Admin"
    ["18100"]="Fluentd"
    ["18110"]="Weaviate"
    ["18170"]="MinIO API"
    ["18171"]="MinIO Console"
)

# Check each expected port
total_ports=0
running_ports=0

for port in "${!expected_services[@]}"; do
    total_ports=$((total_ports + 1))
    service_name="${expected_services[$port]}"

    if ss -tlnp | grep -q ":$port "; then
        echo -e "${GREEN}✅${NC} Port $port - $service_name"
        running_ports=$((running_ports + 1))

        # Show process details
        process=$(ss -tlnp | grep ":$port " | awk '{print $7}' | cut -d',' -f1 | cut -d'=' -f2)
        if [[ -n "$process" ]]; then
            echo "   Process: $process"
        fi
    else
        echo -e "${RED}❌${NC} Port $port - $service_name (NOT LISTENING)"
    fi
done

# Check for any unexpected 18xxx ports
echo
echo -e "${YELLOW}=== Checking for unexpected 18xxx ports ===${NC}"
unexpected_ports=$(ss -tlnp | grep ':18' | awk '{print $4}' | cut -d':' -f2 | sort -u | while read port; do
    if [[ -z "${expected_services[$port]:-}" ]]; then
        echo "$port"
    fi
done)

if [[ -n "$unexpected_ports" ]]; then
    echo -e "${YELLOW}⚠️  Unexpected 18xxx ports found:${NC}"
    for port in $unexpected_ports; do
        echo "   Port $port - Unknown service"
        ss -tlnp | grep ":$port " | head -1
    done
else
    echo -e "${GREEN}✅ No unexpected 18xxx ports found${NC}"
fi

# Summary
echo
echo -e "${BLUE}=== Summary ===${NC}"
echo "Total expected ports: $total_ports"
echo "Running ports: $running_ports"
echo "Success rate: $(( running_ports * 100 / total_ports ))%"

if [[ $running_ports -eq $total_ports ]]; then
    echo -e "${GREEN}🎉 All expected 18xxx services are running!${NC}"
    exit 0
else
    echo -e "${YELLOW}⚠️  Some services are not running. Check the list above.${NC}"
    exit 1
fi