# Architecture Documentation

## System Design Overview

### High-Level Data Flow

```
┌──────────────────────────────────────────────────────────────┐
│                      DATA INGESTION                          │
│                    (RandomUser API)                          │
│  Fetches: Name, Email, Phone, Demographics, Location        │
└──────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────────┐
│                    ORCHESTRATION LAYER                       │
│                    (Apache Airflow)                          │
│  • DAG Scheduling                                            │
│  • Data Transformation Pipeline                             │
│  • Error Handling & Retries                                 │
│  • Dependency Management                                    │
└──────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────────┐
│                    MESSAGE BROKER LAYER                      │
│                    (Apache Kafka)                            │
│  Topic: users_topic                                          │
│  • Partitions: 3 (default)                                  │
│  • Replication Factor: 1                                    │
│  • Retention: Based on configuration                        │
└──────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────────┐
│                  STREAM PROCESSING LAYER                     │
│                    (Apache Spark)                            │
│  • Real-time stream processing                              │
│  • Data transformation & enrichment                         │
│  • Aggregations & windowing                                 │
│  • Data quality validation                                  │
└──────────────────────────────────────────────────────────────┘
                             │
                ┌────────────┴────────────┐
                ▼                         ▼
    ┌─────────────────────┐   ┌────────────────────┐
   │   STORAGE LAYER     │   │  STORAGE LAYER     │
   │ PostgreSQL (Metadata│   │    Cassandra       │
   │     only)           │   │  • Time-Series     │
   │  • Metadata store   │   │  • High Throughput │
   │  • Airflow &        │   │  • Distributed     │
   │    Superset metadata│   │  • NoSQL Model     │
   │  • Not used for     │   │                    │
   │    application OLTP │   │                    │
    └─────────────────────┘   └────────────────────┘
                │                       │
                └───────────┬───────────┘
                            ▼
    ┌──────────────────────────────────────┐
    │     VISUALIZATION LAYER              │
    │       (Apache Superset)              │
    │  • Interactive Dashboards            │
    │  • Real-time Analytics               │
    │  • Data Exploration                  │
    │  • Custom Metrics                    │
    └──────────────────────────────────────┘
```

---

## Component Architecture

### 1. Airflow Orchestration

**Purpose:** Workflow scheduling and orchestration

**Key Configuration:**
- Executor: Sequential (default) or Distributed
- Scheduler: Parses DAGs every 30 seconds
- Metadata DB: PostgreSQL

**DAG Structure:**
```
kafka_stream (DAG)
├── get_data_task
│   └── Fetches from RandomUser API
├── format_data_task
│   └── Structures raw data
├── stream_data_task
│   ├── Produces to Kafka
│   └── Kafka Topic: users_topic
└── Processing continues in Spark
```

**Connection Details:**
- Database: `airflow` on PostgreSQL
- User: `airflow`
- Network: `airflow-network`

---

### 2. Kafka Message Broker

**Purpose:** Decoupled, scalable event streaming

**Topics:**
- `users_topic`: Raw user data from API
  - Partitions: 3
  - Replication: 1
  - Retention: 24 hours (configurable)

**Data Format:**
```json
{
  "first_name": "John",
  "last_name": "Doe",
  "email": "john@example.com",
  "gender": "male",
  "dob": "1990-01-15T10:30:00Z",
  "age": 34,
  "phone": "+1-555-0100",
  "nationality": "US",
  "address": "123 Main St, New York, NY, USA",
  "picture": "https://..."
}
```

**Connection Details:**
- Bootstrap Servers: `broker:9092`
- ZooKeeper: `zookeeper:2181`
- Schema Registry: `schema-registry:8081` (for Avro/Schema management)
- Control Center: `control-center:9021` (optional monitoring/UI)
- Network: `confluent`

---

### 3. Spark Processing

**Purpose:** Real-time stream processing and transformation

**Processing Pipeline:**
1. Read from Kafka topic
2. Parse JSON messages
3. Apply transformations
4. Data quality checks
5. Write application data to Cassandra (or other OLTP/OLAP storage).
   PostgreSQL is only used as metadata DB for Airflow and Superset and
   is not used as the primary OLTP store for application data.

**Spark Configuration:**
- Master: `spark://spark-master:7077`
- UI: http://localhost:4040
- Memory: 2GB (configurable)

**Network:** `spark-network`

---

### 4. PostgreSQL Database (Metadata only)

**Purpose:** Metadata store for orchestration and visualization platforms. PostgreSQL
is used only for metadata for Airflow and Superset (DAG metadata, user/session
information, Superset metadata). It is explicitly not used as the primary
OLTP store for application/data pipeline output.

**Schema:**
```
Database: airflow
├── alembic_version
├── dag_run
├── task_instance
└── ... (Airflow metadata tables)

Database: superset
├── ab_user
├── slices
├── dashboards
└── ... (Superset metadata tables)
```

**Key Tables (examples):**
- Airflow: `dag`, `task_instance`, `dag_run`, `xcom` (metadata)
- Superset: `ab_user`, `dashboards`, `slices`, `tables` (metadata)

**Properties:**
- Type: Relational SQL Database (metadata)
- ACID Compliance: Yes (important for metadata integrity)
- Replication: Single instance (can be upgraded to replicas for HA)
- Connection Pool: tuned for metadata workloads (small, frequent queries)
- Network: reachable by `airflow` and `superset` services only

**Notes:**
- Application OLTP and large-scale analytical data should be stored in
   dedicated OLTP/OLAP systems (e.g., Cassandra, object storage, or a
   separate production DB). Do not store application event data or bulk
   user/profile records in this PostgreSQL instance.

---

### 5. Cassandra Database

**Purpose:** NoSQL time-series storage (OLAP)

**Keyspaces:**
```
user_events
├── user_events (table)
│   ├── event_id (UUID, PRIMARY KEY)
│   ├── user_id
│   ├── event_type
│   ├── timestamp
│   └── event_data (MAP)
└── user_sessions (table)
```

**Properties:**
- Type: NoSQL Distributed Database
- Replication Factor: 1 (default)
- Consistency Level: ONE
- Partitioning: Event ID based
- Network: `spark-network`

---

### 6. Superset BI Platform

**Purpose:** Data visualization and dashboards

**Databases Connected:**
- PostgreSQL (superset metadata only)
- Cassandra (as a data source for analytical dashboards)
\- Other datasource connectors may be added (e.g., object storage, Redshift)

**Features:**
- Drag-and-drop dashboard builder
- SQL query editor
- Real-time data refresh
- Custom aggregations
- User/permission management

**Configuration:**
- Port: 8088
- User: admin (default)
- Database URI: PostgreSQL
- Cache: File-based (in-container)

---

## Network Architecture

### Docker Networks

```yaml
Networks:
  airflow-network (bridge)
  ├── airflow-webserver
  ├── airflow-scheduler
  ├── postgres
  └── redis (optional)
  
  spark-network (bridge)
  ├── spark-master
  ├── spark-worker
  └── cassandra
  
  superset-network (bridge)
  ├── superset
  ├── redis (optional)
  └── postgres
  
  confluent (default)
  ├── broker (Kafka)
  └── zookeeper
```

### Service Communication

| From | To | Port | Protocol |
|------|----|----|----------|
| Airflow | Kafka | 9092 | TCP |
| Airflow | PostgreSQL | 5432 | TCP |
| Spark | Kafka | 9092 | TCP |
| Spark | Cassandra | 9042 | CQL |
| Superset | PostgreSQL (metadata) | 5432 | TCP |
| Superset | Cassandra (data source) | 9042 | CQL |

---

## Scalability Considerations

### Horizontal Scaling

**Airflow:**
- Add multiple scheduler instances
- Use Celery or Kubernetes executor
- Scale web server with load balancer

**Kafka:**
- Increase broker count
- Add partitions to topics
- Adjust replication factor

**Spark:**
- Add worker nodes
- Increase executor count/memory
- Tune parallelism settings

**PostgreSQL:**
- Read replicas
- Streaming replication
- Partitioning (if needed)

**Cassandra:**
- Add nodes to cluster
- Increase replication factor
- Geographic distribution

---

## Data Consistency & Reliability

### Fault Tolerance

| Component | Strategy |
|-----------|----------|
| Airflow | DAG retry logic, backfill capability |
| Kafka | Replication, multiple partitions |
| Spark | Checkpointing, fault-tolerant RDDs |
| PostgreSQL | WAL (Write-Ahead Logging), backups |
| Cassandra | Replication, hinted handoff |

### Data Quality Checks

1. **Schema Validation**
   - Verify required fields present
   - Type checking
   - Format validation

2. **Completeness Checks**
   - No null values in critical fields
   - All records have timestamps

3. **Consistency Checks**
   - No duplicate events
   - Data matches expected ranges

4. **Freshness Checks**
   - Data latency < threshold
   - Pipeline SLA compliance

---

## Monitoring & Observability

### Metrics to Monitor

**Airflow:**
- DAG success/failure rates
- Task duration
- Scheduler health
- Web server responsiveness

**Kafka:**
- Consumer lag
- Broker CPU/Memory
- Message throughput
- Error rate

**Spark:**
- Task completion time
- Shuffle data
- Memory usage
- Number of tasks

**Databases:**
- Query latency
- Connection pool usage
- Disk I/O
- Replication lag

**Superset:**
- Dashboard load time
- Query execution time
- User sessions

### Health Checks

```bash
# Airflow
curl http://localhost:8080/health

# Kafka
docker exec broker kafka-broker-api-versions.sh --bootstrap-server localhost:9092

# PostgreSQL
docker exec postgres pg_isready -U airflow

# Cassandra
docker exec cassandra nodetool status

# Superset
curl http://localhost:8088/health
```

---

## Technology Choices & Rationale

| Technology | Why |
|------------|-----|
| Kafka | Real-time streaming, decoupling, fault tolerance |
| Spark | Distributed processing, multiple data sources/sinks |
| PostgreSQL | ACID, complex queries, data integrity |
| Cassandra | Time-series optimized, high write throughput |
| Airflow | Complex DAGs, scheduling, monitoring |
| Superset | Rich dashboards, SQL support, extensible |
| Docker | Reproducibility, easy deployment, isolation |

---

## Future Enhancements

- [ ] Add data validation framework
- [ ] Implement real-time alerting
- [ ] Add API gateway
- [ ] Cloud-native deployment (Kubernetes)
- [ ] Multi-region setup
- [ ] Advanced monitoring (ELK, Prometheus)
- [ ] ML pipeline integration

---

**Architecture Version:** 1.0  
**Last Updated:** 2026-02-02
