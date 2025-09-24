# Issues Fixes and Resolutions

## SystemD Namespace Issues (226/NAMESPACE)

### Problem
Multiple database services were failing with `exit-code status=226/NAMESPACE` errors when starting via SystemD. This was caused by overzealous security hardening directives that were incompatible with the actual runtime environment.

### Root Cause
The SystemD service files contained restrictive security settings that prevented proper namespace isolation:
- `ProtectSystem=strict` without proper `ReadWritePaths`
- `ProtectHome=true` blocking access to necessary directories
- `PrivateTmp=true` causing permission issues
- `NoNewPrivileges=true` preventing proper process execution

### Solution
Applied minimal security hardening approach, then services were successfully started:

#### Weaviate Fix
```bash
# Created minimal SystemD service file with relaxed security:
[Service]
Type=simple
User=x
Group=x
WorkingDirectory=/data/databases/data/weaviate
ExecStart=/usr/local/bin/weaviate --host 0.0.0.0 --port 18060 --scheme http
Restart=on-failure
# relax hardening to avoid status=226/NAMESPACE; re-enable later, surgically
PrivateTmp=false
ProtectSystem=off
ProtectHome=off
NoNewPrivileges=false
```

#### Trino Fix
```bash
# Fixed launcher command and user configuration:
[Service]
Type=simple
User=trino
Group=trino
WorkingDirectory=/opt/trino/current
ExecStart=/opt/trino/current/bin/launcher run
Restart=on-failure
# relax hardening to avoid status=226/NAMESPACE; tune later
PrivateTmp=false
ProtectSystem=off
ProtectHome=off
NoNewPrivileges=false
```

### Resolution
All services now running successfully with minimal security hardening. Hardening can be re-enabled incrementally once service stability is confirmed.

---

## Java Version Compatibility Issues

### Problem
Trino 476 requires Java 22+ but Ubuntu 24.04 only provides Java 21 through official repositories. This caused `UnsupportedClassVersionError` when trying to start Trino.

### Root Cause
- Trino 476 was compiled with Java 24 (class file version 68.0)
- System only had Java 21 available (class file version 66.0)
- Version mismatch prevented class loading

### Solution
Installed Java 24 from official Eclipse Temurin builds:

```bash
# Download and install Java 24
sudo mkdir -p /opt/java-24
cd /tmp && wget -q -O jdk-24.tar.gz https://github.com/adoptium/temurin24-binaries/releases/download/jdk-24.0.2%2B12/OpenJDK24U-jdk_x64_linux_hotspot_24.0.2_12.tar.gz
sudo tar -xzf /tmp/jdk-24.tar.gz -C /opt/java-24 --strip-components=1
sudo chown -R root:root /opt/java-24

# Register as system alternative
sudo update-alternatives --install /usr/bin/java java /opt/java-24/bin/java 2424
sudo update-alternatives --set java /opt/java-24/bin/java
```

### Resolution
Trino now starts successfully with Java 24. All Java-based services are compatible with the new runtime.

---

## Network Connectivity Issues

### Problem
Initial package installation failures due to DNS resolution issues with various repositories:
- Redpanda GPG key repository unreachable
- Weaviate GitHub downloads failing
- Trino Maven repository timeouts
- Fluentd repository paths incorrect

### Root Cause
- Temporary network connectivity issues
- Incorrect repository URLs
- Missing GPG keys for package verification

### Solution
- Waited for network connectivity to be restored
- Used correct repository URLs and installation methods
- Implemented official vendor installation scripts where available

### Resolution
All packages successfully installed once network connectivity was restored.

---

## Repository and Package Management Issues

### Problem
- Trino doesn't provide official APT repositories
- Fluentd has multiple installation methods with different package names
- Some services require manual installation from source binaries

### Solution
- Used tarball installation for Trino with proper SystemD service configuration
- Used official `fluent-package` installer for Fluentd
- Created proper user accounts and directory structures for manual installations

### Resolution
All services properly installed and configured with SystemD service management.

---

## Service Configuration Issues

### Problem
- Incorrect launcher commands in SystemD service files
- Missing configuration directories and files
- Improper user permissions and directory ownership

### Solution
- Fixed Trino to use `launcher run` instead of `launcher start/stop`
- Created proper configuration files for all services
- Established correct user accounts (trino, td-agent) with proper permissions
- Created necessary directories with correct ownership

### Resolution
All services now start correctly with proper configuration and permissions.

---

## Port Assignment and Configuration

### Problem
Services needed to be configured to use 18xx port block as requested, but some services use default ports for compatibility.

### Solution
- Configured services to use 18xx ports where possible:
  - DragonFly: 18001
  - Neo4j: 18040-18042
  - Weaviate: 18060
  - Trino: 18080
  - Fluentd: 18100
- Left PostgreSQL on 5432 for application compatibility
- Left Redpanda on default ports 9092/8081 for Kafka compatibility

### Resolution
All services properly configured with appropriate port assignments while maintaining compatibility.

---

## Lessons Learned

1. **Start with minimal security hardening** - Add security restrictions incrementally after confirming basic functionality
2. **Verify Java version requirements** - Some modern applications require newer Java versions than available in system repositories
3. **Use official vendor installation methods** - Always prefer vendor-recommended installation procedures
4. **Check service logs immediately** - SystemD namespace errors provide clear indicators of configuration issues
5. **Proper user and directory setup** - Manual installations require careful attention to user accounts and permissions
6. **Network connectivity is essential** - Package installation may fail temporarily due to network issues

## Future Considerations

1. **Incremental Security Hardening** - Once services are stable, gradually re-enable security features with proper configuration
2. **Monitoring and Alerting** - Implement health checks and monitoring for all services
3. **Backup and Recovery** - Establish backup procedures for all database services
4. **Performance Tuning** - Optimize configurations based on actual workload requirements
5. **Documentation Updates** - Keep service documentation current with configuration changes