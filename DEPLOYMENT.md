# Production Deployment Guide

Guide for deploying the E2E Big Data Pipeline to production environments.

---

## Pre-Deployment Checklist

- [ ] Security audit completed
- [ ] Data backup strategy defined
- [ ] Monitoring & alerting configured
- [ ] Disaster recovery plan created
- [ ] Load testing completed
- [ ] Documentation updated
- [ ] Team trained on operations

---

## Architecture Considerations

### High Availability

```yaml
# Multi-node setup example
airflow:
  - webserver (load balanced)
  - scheduler (HA-enabled)
  - worker pool (scalable)

kafka:
  - brokers: 3+
  - replication: 2+
  - partitions: at least brokers count

spark:
  - master: HA-enabled or Kubernetes
  - workers: auto-scaling group

postgres:
  - primary + replica
  - streaming replication
  - automated failover

cassandra:
  - cluster: 3+ nodes
  - replication_factor: 3
  - consistency_level: QUORUM
```

### Network Architecture

```
┌─────────────────────────────────────────┐
│         Load Balancer / Ingress         │
│    (Nginx / HAProxy / Cloud Provider)   │
└────────────┬────────────────────────────┘
             │
    ┌────────┴────────┐
    │                 │
┌───▼────┐      ┌────▼───┐
│Airflow │      │Superset│
│ (x3)   │      │ (x3)   │
└───┬────┘      └────┬───┘
    │                │
    └────────┬───────┘
             │
    ┌────────▼────────┐
    │  PostgreSQL HA  │
    │ (Primary+Standby)
    └────────┬────────┘
             │
    ┌────────┼────────┐
    │        │        │
┌───▼──┐ ┌──▼────┐ ┌─▼────┐
│Kafka │ │Spark  │ │Cassandra
│ (x3) │ │ (x3)  │ │(x3+)
└──────┘ └───────┘ └──────┘
```

---

## Cloud Deployment

### AWS Deployment

**Services Used:**
- ECS/EKS (Container orchestration)
- RDS (PostgreSQL)
- MSK (Managed Kafka)
- EMR (Spark clusters)
- CloudWatch (Monitoring)

**Terraform Configuration (Example):**
```hcl
# main.tf
module "postgres" {
  source = "./modules/postgres"
  
  engine           = "postgres"
  version          = "16"
  instance_class   = "db.t3.large"
  allocated_storage = 100
  multi_az         = true
  
  backup_retention_period = 30
}

module "airflow_ecs" {
  source = "./modules/airflow"
  
  container_image  = "your-registry/airflow:latest"
  cpu              = 1024
  memory           = 2048
  desired_count    = 3
  
  depends_on = [module.postgres]
}
```

### Kubernetes Deployment

**Helm Charts:**
```bash
# Add repositories
helm repo add apache-airflow https://airflow.apache.org
helm repo add bitnami https://charts.bitnami.com/bitnami

# Install Airflow
helm install airflow apache-airflow/airflow \
  -f values-production.yaml

# Install PostgreSQL
helm install postgres bitnami/postgresql \
  -f postgres-values.yaml

# Install Kafka
helm install kafka bitnami/kafka \
  -f kafka-values.yaml
```

---

## Security Implementation

### SSL/TLS Configuration

```yaml
# PostgreSQL SSL
postgresql:
  environment:
    - POSTGRES_INITDB_ARGS=-c ssl=on

# Airflow SSL
airflow:
  webserver:
    web_server_ssl_cert: /path/to/cert.pem
    web_server_ssl_key: /path/to/key.pem

# Superset SSL
superset:
  flask_ssl_context: adhoc
```

### Authentication & Authorization

```python
# Airflow RBAC
airflow:
  rbac:
    rbac_enabled: True
    auth_backend: airflow.contrib.auth.backends.ldap_auth

# Superset Authentication
SUPERSET_WEBSERVER_AUTH_TYPE = AUTH_LDAP
# or
SUPERSET_WEBSERVER_AUTH_TYPE = AUTH_OAUTH
```

### Network Security

```yaml
# VPC Configuration
vpc:
  cidr: 10.0.0.0/16
  
security_groups:
  airflow:
    ingress:
      - port: 8080
        source: office_ip_range
      - port: 443
        source: 0.0.0.0/0
  
  postgres:
    ingress:
      - port: 5432
        source: app_security_group
  
  kafka:
    ingress:
      - port: 9092
        source: internal_vpc
```

---

## Database Configuration

### PostgreSQL Production Setup

```sql
-- Create replication user
CREATE USER replicator WITH REPLICATION LOGIN ENCRYPTED PASSWORD 'strong_password';

-- Configure backup
-- Use pg_basebackup or WAL archiving
-- Set up streaming replication

-- Performance tuning
ALTER SYSTEM SET shared_buffers = '16GB';
ALTER SYSTEM SET work_mem = '64MB';
ALTER SYSTEM SET maintenance_work_mem = '4GB';
ALTER SYSTEM SET effective_cache_size = '48GB';
ALTER SYSTEM SET max_wal_size = '4GB';
ALTER SYSTEM SET random_page_cost = 1.1;

SELECT pg_reload_conf();
```

### Cassandra Production Setup

```cql
-- Check cluster status
NODETOOL STATUS;

-- Configure replication
ALTER KEYSPACE user_events 
WITH REPLICATION = {
  'class': 'NetworkTopologyStrategy',
  'dc1': '3'
};

-- Monitor performance
NODETOOL TPSTATS;
NODETOOL NETSTATS;
```

---

## Monitoring & Observing

### Prometheus Metrics

```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'airflow'
    static_configs:
      - targets: ['airflow-webserver:8793']
  
  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres-exporter:9187']
  
  - job_name: 'cassandra'
    static_configs:
      - targets: ['cassandra-exporter:7200']
```

### ELK Stack Integration

```yaml
# filebeat.yml
filebeat.inputs:
  - type: log
    enabled: true
    paths:
      - /var/log/airflow/*.log
      - /var/log/cassandra/*.log
      - /var/log/postgresql/*.log

output.elasticsearch:
  hosts: ["elasticsearch:9200"]

processors:
  - add_kubernetes_metadata:
      in_cluster: true
```

### Alerts Configuration

```yaml
# alerting_rules.yml
groups:
  - name: airflow
    rules:
      - alert: DAGFailureRate
        expr: rate(airflow_dag_failure_count[5m]) > 0.1
        for: 5m
        annotations:
          summary: "High DAG failure rate"
      
      - alert: PostgreSQLDown
        expr: pg_up == 0
        for: 1m
        annotations:
          summary: "PostgreSQL instance down"
```

---

## Backup & Disaster Recovery

### Backup Strategy

```bash
#!/bin/bash
# Daily backup script

BACKUP_DIR="/backups/$(date +%Y%m%d)"
mkdir -p $BACKUP_DIR

# PostgreSQL backup
pg_basebackup -h postgres -U replicator \
  -D $BACKUP_DIR/postgres \
  -Ft -z -P

# Kafka topics backup
for topic in $(kafka-topics.sh --list); do
  kafka-mirror-maker.sh \
    --consumer.config source.conf \
    --producer.config dest.conf \
    --whitelist "$topic"
done

# Cassandra snapshots
nodetool snapshot -t backup_$(date +%Y%m%d) user_events

# Upload to cloud storage
aws s3 sync $BACKUP_DIR s3://backup-bucket/
```

### Restore Procedures

```bash
# PostgreSQL restore
pg_basebackup -h postgres_new \
  -D /data/postgres \
  -R

# Cassandra restore
nodetool restore backup_id

# Kafka topics restore from backup
kafka-mirror-maker.sh \
  --consumer.config backup.conf \
  --producer.config prod.conf \
  --whitelist ".*"
```

---

## Performance Tuning

### Airflow Optimization

```python
# airflow.cfg
[core]
parallelism = 32
dag_concurrency = 16
max_active_tasks_per_dag = 16
max_active_runs_per_dag = 16

[scheduler]
max_dagruns_to_create_per_loop = 10
catchup_by_default = False

[webserver]
expose_config = False
rbac = True
```

### Spark Optimization

```python
spark = SparkSession.builder \
    .appName("data_pipeline") \
    .config("spark.driver.memory", "4g") \
    .config("spark.executor.memory", "8g") \
    .config("spark.executor.cores", "4") \
    .config("spark.sql.shuffle.partitions", "200") \
    .config("spark.dynamicAllocation.enabled", "true") \
    .getOrCreate()
```

---

## CI/CD Integration

### GitHub Actions Example

```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Test Docker build
        run: docker compose up --build
      - name: Run tests
        run: docker compose exec -T airflow pytest

  deploy:
    needs: test
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to AWS
        run: terraform apply -auto-approve
```

---

## Operational Runbooks

### Daily Operations

**Morning Checklist:**
```bash
# Check all services
docker compose ps

# Verify data flow
docker exec broker kafka-consumer-groups.sh \
  --list --bootstrap-server localhost:9092

# Check Airflow DAGs
curl http://airflow:8080/api/v1/dags | jq '.dags[] | select(.is_paused==false)'

# Monitor disk usage
df -h /data/*
```

**Evening Procedures:**
```bash
# Backup critical data
./scripts/backup.sh

# Verify replication lag
nodetool status

# Check error logs
docker compose logs | grep ERROR
```

---

## Scaling Guidelines

### When to Scale

| Metric | Threshold | Action |
|--------|-----------|--------|
| Airflow task queue | 1000+ tasks | Add scheduler |
| Kafka consumer lag | > 30 seconds | Increase partitions |
| Spark execution time | > SLA | Add executors |
| PostgreSQL connections | > 80% | Add replicas |
| Cassandra disk usage | > 80% | Add nodes |

---

## Troubleshooting Production Issues

### Memory Leak Detection

```bash
# Monitor memory over time
docker stats --no-stream --format \
  "table {{.Container}}\t{{.MemUsage}}" \
  | tee memory_log.txt

# Analyze trends
awk '{print $NF}' memory_log.txt | sort | uniq -c
```

### Network Bottleneck Detection

```bash
# Monitor network I/O
iftop -i eth0

# Check Kafka network metrics
kafka-consumer-perf-test.sh \
  --broker-list localhost:9092 \
  --topic users_topic
```

---

## Support & Escalation

**Escalation Path:**
1. Check application logs
2. Review monitoring alerts
3. Consult runbooks
4. Contact on-call engineer
5. Engage vendor support

---

**Last Updated:** 2026-02-02

For emergencies, contact: ops-team@company.com
