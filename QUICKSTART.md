# Quick Start Guide

Get up and running with the E2E Big Data Pipeline in minutes.

## Prerequisites Checklist

- [ ] Docker installed (v20.10+): https://docs.docker.com/get-docker/
- [ ] Docker Compose installed (v2.0+): Included with Docker Desktop
- [ ] 8GB+ RAM available
- [ ] 10GB+ free disk space
- [ ] Git installed

**Verify installation:**
```bash
docker --version
docker compose --version
git --version
```

---

## Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/E2E.git
cd E2E
```

---

## Step 2: Configure Environment

The default `.env` files are pre-configured. Optional customization:

```bash
# Customize Superset
vi superset/docker/.env

# Customize PostgreSQL
vi postgres/.env

# Customize Airflow
vi airflow/docker-compose.yml
```

---

## Step 3: Start Services

```bash
# Start all services in background
docker compose up -d

# Watch the startup progress
docker compose logs -f
```

**First run takes 2-5 minutes** for services to initialize.

---

## Step 4: Verify Services

```bash
# Check all services are running
docker compose ps
```

Expected output:
```
NAME                 STATUS
airflow-webserver    Up
airflow-scheduler    Up
postgres             Up (healthy)
broker               Up
zookeeper            Up
cassandra            Up
spark-master         Up
superset-app         Up
```

---

## Step 5: Access Services

| Service | URL | Default Credentials |
|---------|-----|-------------------|
| **Airflow** | http://localhost:8080 | airflow / airflow |
| **Superset** | http://localhost:8088 | admin / admin |
| **Spark UI** | http://localhost:4040 | — / — |
| **Kafka Broker** | localhost:9092 | — / — |

---

## Step 6: Trigger Your First DAG

1. **Open Airflow UI** → http://localhost:8080
2. **Login** with airflow / airflow
3. **Find DAG** → `kafka_stream`
4. **Enable it** → Toggle the DAG to ON
5. **Trigger it** → Click ▶️ (play icon)
6. **Monitor** → Watch tasks execute in real-time

---

## Step 7: Create Superset Dashboard

1. **Open Superset** → http://localhost:8088
2. **Login** with admin / admin
3. **Add Database** (if not auto-connected):
   - Type: PostgreSQL
   - Host: postgres
   - Port: 5432
   - User: superset
   - Password: superset
   - Database: superset_db
4. **Create Dataset** from `public.users` table
5. **Build Dashboard** with charts and metrics

---

## Common Tasks

### View Logs

```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f airflow-scheduler
docker compose logs -f broker
docker compose logs -f spark-master
```

### Stop Services

```bash
# Stop (keep data)
docker compose stop

# Stop and remove containers
docker compose down
```

### Restart Services

```bash
# Restart all
docker compose restart

# Restart specific service
docker compose restart postgres
docker compose restart airflow-webserver
```

### Execute Commands in Container

```bash
# List Kafka topics
docker exec broker kafka-topics.sh --list --bootstrap-server localhost:9092

# Access PostgreSQL
docker exec postgres psql -U airflow -d airflow

# Spark shell
docker exec spark-master spark-shell

# Cassandra shell
docker exec cassandra cqlsh
```

---

## Troubleshooting

### Service won't start

```bash
# Check container logs
docker compose logs postgres

# Restart service
docker compose restart postgres

# Full reset
docker compose down -v
docker compose up -d
```

### Can't access Airflow/Superset

- Wait 30-60 seconds (first initialization takes time)
- Check container is running: `docker compose ps airflow-webserver`
- Check logs: `docker compose logs airflow-webserver`

### Database connection error

```bash
# Verify database is running
docker compose exec postgres pg_isready -U airflow

# Check connectivity from another container
docker compose exec airflow-webserver bash -c \
  "psql -h postgres -U airflow -d airflow -c 'SELECT 1;'"
```

### Kafka not receiving messages

```bash
# Check topic exists
docker exec broker kafka-topics.sh \
  --list --bootstrap-server localhost:9092

# Check messages
docker exec broker kafka-console-consumer.sh \
  --topic users_topic \
  --bootstrap-server localhost:9092 \
  --from-beginning | head -5
```

---

## Next Steps

1. **Explore Airflow**
   - View DAG runs and task logs
   - Trigger manual runs
   - Understand dependencies

2. **Check Data Flow**
   - Verify Kafka messages
   - Query PostgreSQL tables
   - Explore Cassandra data

3. **Build Dashboards**
   - Create datasets in Superset
   - Build visualizations
   - Share dashboards

4. **Monitor Pipeline**
   - Check Airflow logs
   - Monitor resource usage
   - Set up alerts

5. **Customize**
   - Modify Airflow DAGs
   - Adjust Spark processing
   - Create custom dashboards

---

## Performance Tips

- **Airflow:** Increase `parallelism` in `airflow.cfg` for more concurrent tasks
- **Kafka:** Add partitions to `users_topic` for higher throughput
- **Spark:** Increase executor memory in `docker-compose.yml`
- **PostgreSQL:** Adjust `shared_buffers` and `work_mem` in configuration
- **Cassandra:** Increase `heap_size` for large datasets

---

## Security Considerations

⚠️ **Default credentials are for development only!**

Before production:
- [ ] Change all default passwords
- [ ] Enable SSL/TLS for all connections
- [ ] Use environment-specific `.env` files
- [ ] Implement network policies
- [ ] Enable authentication on Kafka
- [ ] Set up access controls in Superset

---

## Clean Up

```bash
# Stop all services
docker compose stop

# Remove containers (keep data)
docker compose rm

# Remove everything including volumes
docker compose down -v

# Remove unused Docker resources
docker system prune -a
```

---

## Getting Help

- 📖 Full documentation: [README.md](README.md)
- 🏗️ Architecture details: [ARCHITECTURE.md](ARCHITECTURE.md)
- 🔧 Troubleshooting: [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- 🐛 Report issues: GitHub Issues
- 💬 Discuss: GitHub Discussions

---

**Happy data engineering!** 🚀
