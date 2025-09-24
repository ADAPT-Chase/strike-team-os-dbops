# DBOps - Database Operations Repository

**Mission**: Keep prod boring, audits happy, and 3 a.m. you asleep.

## Guiding Principles

- One repo to operate many engines. Per-engine overrides, shared standards.
- Everything reproducible from a commit: config + topology + seed + restore drill.
- Backups are guilty until proven restorable. DR is code, not folklore.
- Changes flow through migrations, runbooks, and gates. No "one-liners" in prod.
- Observability, SLOs, and capacity planning are first-class. Feelings are not metrics.

## Quick Start

1. **Current Services**: PostgreSQL, Redis Cluster, DragonFly, Qdrant, MinIO, Redpanda, Neo4j, Weaviate, Trino, Fluentd
2. **All configs**: In `/configs/` with env-specific overlays
3. **Operations**: Use scripts in `/scripts/` with guardrails
4. **Monitoring**: Dashboards in `/observability/`, alerts wired to pager

## Repository Structure

```
├── .github/                    # CI, CODEOWNERS, PR templates
├── docs/                       # High-level docs & policies
├── configs/                    # Per-engine configs with env overlays
├── topologies/                 # Cluster maps, inventories, capacity models
├── runbooks/                   # How to do anything without breaking everything
├── migrations/                 # DDL, data fixes, idempotent scripts
├── backups/                    # Backup + restore-as-code
├── cdc/                        # Change data capture connectors & schemas
├── observability/              # Metrics, logs, traces, dashboards, alerts
├── security/                   # RBAC templates, audit, key rotation
├── maintenance/                # Routine jobs: vacuum, repair, compaction
├── tests/                      # Config lint, migration tests, backup drills
├── benchmarks/                 # Reproducible perf tests
├── scripts/                    # Admin ergonomics with guardrails
├── infra/                      # systemd units, sysctl, ulimits, disk profiles
├── risk/                       # Data classification, retention, incident templates
├── ci/                         # Shared CI helpers for multi-engine test matrix
└── third_party/                # Vendored exporters/utilities
```

## Supported Engines

- **PostgreSQL/TimescaleDB** - Relational + time-series
- **Redis/DragonFly** - In-memory caching & clustering
- **Qdrant** - Vector database
- **MinIO** - S3-compatible object storage
- **Redpanda** - Kafka-compatible streaming platform
- **Neo4j** - Graph database
- **Weaviate** - AI vector database
- **Trino** - Distributed SQL query engine
- **Fluentd** - Log collection and processing

## Engine Status

| Engine | Version | Ports | Status | Health |
|--------|---------|-------|--------|--------|
| PostgreSQL | 16 | 5432 | ✅ Running | OK |
| TimescaleDB | Extension | - | ✅ Active | OK |
| Redis Cluster | 7.x | 18010-18012 | ✅ Running | OK |
| DragonFly | Latest | 18001 | ✅ Running | OK |
| Qdrant | 1.15.4 | 18001-18002 | ⚠️ Port Conflict | Needs Fix |
| Redpanda | 25.2.5 | 9092, 8081 | ✅ Running | OK |
| Neo4j | Latest | 18040-18042 | ✅ Running | OK |
| Weaviate | Latest | 18060 | ✅ Running | OK |
| Trino | 476 | 18080 | ✅ Running | OK |
| Fluentd | Latest | 18100 | ✅ Running | OK |

## Getting Started

1. Review `/docs/standards.md` for naming and conventions
2. Check `/configs/` for your engine-specific configurations
3. Run `./scripts/dbops health` to verify all services
4. Consult `/runbooks/` for operational procedures

## On-Call & Escalation

- **Primary**: Systems Team
- **Secondary**: Database Architects
- **Emergency**: Chief Systems Architect

**Last Updated**: 2025-09-23
**Maintainers**: TeamADAPT Systems Team

## Strike-Team-OS Deployment

### Recent Deployment Summary
- **Date**: 2025-09-23
- **Status**: ✅ Complete - All 7 services successfully deployed
- **Services Added**: Redpanda, Neo4j, Weaviate, Trino, Fluentd
- **Key Issues Resolved**: SystemD namespace conflicts, Java compatibility, network connectivity

### Connection Information
Complete service connection details available in `/data/secrets/strike-team-os-connections.md`

### Issues & Resolutions
Detailed deployment issues and fixes documented in `/data/databases/dbops/issues_fixes.md`

---

**This repo treats prod like a cattle ranch, not a petting zoo.**