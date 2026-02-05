# End-to-End Big Data Pipeline

A complete, production-ready data engineering project demonstrating a modern data pipeline architecture using containerized services.

## 📊 Project Overview

This project implements a comprehensive data pipeline that ingests real-time data, processes it at scale, stores it in multiple databases, and visualizes insights through interactive dashboards.

**Data Flow:**
```
Random User API → Kafka (Message Queue) → Spark (Processing) → PostgreSQL/Cassandra (Storage) → Superset (Visualization)
```

## 🏗️ Architecture

### Components

| Component | Purpose | Technology |
|-----------|---------|-----------|
| **Data Ingestion** | Real-time data streaming | Kafka, Python |
| **Orchestration** | Workflow automation & scheduling | Apache Airflow |
| **Stream Processing** | Real-time data transformation | Apache Spark |
| **Data Storage** | Persistent data storage | PostgreSQL, Cassandra |
| **Visualization** | Business Intelligence dashboards | Apache Superset |
| **Containerization** | Environment standardization | Docker & Docker Compose |

### Service Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    External API                         │
│              (RandomUser.me)                            │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│                  Airflow DAG                            │
│          (Workflow Orchestration)                       │
└─────────────────────────────────────────────────────────┘
                          ↓
┌──────────────────┐    ┌──────────────────┐
│     Kafka        │    │     Spark        │
│  (Message Bus)   │───→│  (Processing)    │
└──────────────────┘    └──────────────────┘
                          ↓
        ┌─────────────────┴─────────────────┐
        ↓                                   ↓
    ┌─────────────┐               ┌────────────────┐
    │ PostgreSQL  │               │   Cassandra    │
    │  (OLTP)     │               │   (NoSQL)      │
    └─────────────┘               └────────────────┘
        ↓                                   ↓
        └─────────────────┬─────────────────┘
                          ↓
                  ┌───────────────┐
                  │   Superset    │
                  │  (Dashboards) │
                  └───────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- Python 3.10+
- Git

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd E2E
```

2. **Start all services**
```bash
docker compose up -d
```

3. **Verify services are running**
```bash
docker compose ps
```

4. **Access the services**
- Airflow UI: http://localhost:8080
- Superset UI: http://localhost:8088
- Kafka: localhost:9092
- PostgreSQL: localhost:5432
- Cassandra: localhost:9042

### Default Credentials

| Service | Username | Password |
|---------|----------|----------|
| Airflow | airflow | airflow |
| Superset | admin | admin |
| PostgreSQL (Airflow) | airflow | airflow |
| PostgreSQL (Superset) | superset | superset |
| Cassandra | — | — |

## 📁 Project Structure

```
E2E/
├── airflow/                      # Airflow orchestration
│   ├── dags/
│   │   └── kafka_stream.py      # Main streaming DAG
│   ├── docker-compose.yml        # Airflow services
│   ├── Dockerfile               # Custom Airflow image
│   ├── requirements.txt          # Python dependencies
│   └── config/
│       └── airflow.cfg          # Airflow configuration
├── kafka/                        # Kafka setup
│   └── docker-compose.yml        # Kafka & Zookeeper services
├── spark/                        # Spark processing
│   └── docker-compose.yml        # Spark services
├── postgres/                     # PostgreSQL database
│   ├── docker-compose.yml
│   ├── airflow_init.sql         # Airflow DB initialization
│   └── superset_init.sql        # Superset DB initialization
├── cassandra/                    # Cassandra NoSQL database
│   └── docker-compose.yml
├── superset/                     # Superset BI platform
│   ├── docker-compose.yml
│   └── docker/
│       ├── superset_config.py    # Superset configuration
│       ├── docker-bootstrap.sh   # Bootstrap script
│       └── .env                  # Environment variables
├── docker-compose.yml            # Root compose (includes all services)
└── scripts/                      # Utility scripts
    └── entrypoint.sh            # Service initialization
```

## 🔄 Data Pipeline Details

### 1. Data Ingestion (Kafka Stream)
The DAG in [airflow/dags/kafka_stream.py](airflow/dags/kafka_stream.py) performs:
- Fetches random user data from RandomUser.me API
- Formats and structures the data
- Produces messages to Kafka topic
- Scheduled to run periodically

**Topics:**
- `users_topic` - Raw user data stream

### 2. Stream Processing (Spark)
Spark jobs consume from Kafka and:
- Apply transformations and data quality checks
- Enrich data with additional attributes
- Write processed data to storage layer

### 3. Data Storage
**PostgreSQL** (Relational):
- Structured user profiles
- Metadata and configurations
- Optimized for OLTP queries

**Cassandra** (NoSQL):
- Time-series user events
- High-write throughput
- Distributed storage for scalability

### 4. Data Visualization (Superset)
Interactive dashboards displaying:
- User demographics
- Activity patterns
- Real-time metrics

## 🛠️ Configuration

### Environment Variables

Key environment files:
- [postgres/.env](postgres/.env) - PostgreSQL configuration
- [superset/docker/.env](superset/docker/.env) - Superset configuration

**Modify these to customize:**
- Database credentials
- Service ports
- Log levels
- Performance tuning parameters

### Airflow Configuration
Edit [airflow/config/airflow.cfg](airflow/config/airflow.cfg) for:
- Parallelism settings
- Executor configuration
- DAG parsing behavior

## 📊 Database Schemas

### PostgreSQL - User Profile Table
```sql
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    first_name VARCHAR(255),
    last_name VARCHAR(255),
    email VARCHAR(255) UNIQUE,
    phone VARCHAR(20),
    nationality VARCHAR(5),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Cassandra - User Events Table
```cql
CREATE TABLE user_events (
    event_id UUID PRIMARY KEY,
    user_id INT,
    event_type TEXT,
    event_data MAP<TEXT, TEXT>,
    timestamp BIGINT,
    created_at TIMESTAMP
);
```

## 🔍 Monitoring & Debugging

### View Logs
```bash
# Airflow logs
docker logs airflow-scheduler

# Spark logs
docker logs spark-master

# Kafka logs
docker logs broker

# PostgreSQL logs
docker logs postgres
```

### Health Checks
```bash
# Check all services
docker compose ps

# Check Kafka broker
docker exec broker kafka-broker-api-versions.sh --bootstrap-server localhost:9092

# Check PostgreSQL connection
psql -h localhost -U airflow -d airflow
```

### Common Issues

**Database Connection Error**
```bash
# Verify network connectivity
docker network inspect e2e_airflow-network

# Restart database
docker compose -f postgres/docker-compose.yml restart
```

**Kafka Producer Issues**
```bash
# Check Kafka broker status
docker logs broker | grep ERROR

# Verify topic exists
docker exec broker kafka-topics.sh --list --bootstrap-server localhost:9092
```

## 🚢 Deployment

### Production Considerations

1. **Security**
   - Use environment-specific .env files
   - Enable SSL/TLS for database connections
   - Implement authentication for all services

2. **Scaling**
   - Increase Spark executor count
   - Configure Cassandra replication factor
   - Set up Kafka partitioning strategy

3. **Monitoring**
   - Implement centralized logging (ELK stack)
   - Add metrics collection (Prometheus)
   - Set up alerting mechanisms

4. **Backup & Recovery**
   - PostgreSQL backup strategy
   - Cassandra snapshot management
   - Kafka topic retention policies

## 📚 Key Technologies

- **Apache Airflow** - Workflow orchestration
- **Apache Kafka** - Event streaming platform
- **Apache Spark** - Distributed data processing
- **PostgreSQL** - Relational database
- **Apache Cassandra** - NoSQL database
- **Apache Superset** - Data visualization
- **Docker & Docker Compose** - Containerization

## 🤝 Contributing

1. Create a feature branch (`git checkout -b feature/improvement`)
2. Make your changes
3. Commit with descriptive messages
4. Push to the branch
5. Open a Pull Request

## 📝 License

This project is open source and available under the MIT License.

## 📧 Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Create a discussion for feature requests

---

**Built with ❤️ for learning and production-ready data engineering**
