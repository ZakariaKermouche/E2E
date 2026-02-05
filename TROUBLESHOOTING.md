# Troubleshooting Guide

## Common Issues & Solutions

### 1. Docker Compose Startup Issues

**Error: "docker: command not found"**
- Install Docker: https://docs.docker.com/get-docker/
- Ensure Docker daemon is running
- On Windows, enable WSL 2 backend

**Error: "Connection refused"**
```bash
# Wait for services to be healthy
docker compose ps  # Check STATUS

# Restart all services
docker compose restart

# Check specific service logs
docker compose logs postgres
docker compose logs kafka
```

---

### 2. Database Connection Errors

**PostgreSQL: "FATAL: database 'superset' does not exist"**
```bash
# Clear volumes and reinitialize
docker compose down -v
docker compose up -d postgres
docker compose up -d superset
```

**PostgreSQL: "Connection refused at 5432"**
```bash
# Verify PostgreSQL is running and healthy
docker compose ps postgres

# Check health status
docker exec postgres pg_isready -U airflow

# View logs
docker compose logs postgres
```

**Cassandra: "Unable to connect"**
```bash
# Cassandra takes time to start (wait 30-60 seconds)
docker compose logs cassandra | grep "Startup complete"

# Check connectivity
docker exec cassandra cqlsh -e "SELECT cluster_name, listen_address FROM system.local;"
```

---

### 3. Airflow Issues

**Airflow UI not accessible at localhost:8080**
- Wait 30 seconds after startup (initialization takes time)
- Check container logs: `docker compose logs airflow-webserver`
- Verify port isn't in use: `netstat -tuln | grep 8080`

**DAG not appearing in Airflow**
```bash
# DAGs are in /airflow/dags directory
# Check parsing errors
docker compose logs airflow-scheduler | grep -i error

# Manually trigger DAG parsing
docker exec airflow-scheduler airflow dags list

# Clear cache and restart
docker compose restart airflow-scheduler
```

**Airflow task fails with connection error**
- Check Kafka broker is running
- Verify network connectivity between containers
- Check firewall rules if running on VM

---

### 4. Kafka Issues

**Kafka broker not responding**
```bash
# Check broker status
docker compose logs broker | tail -20

# Verify broker is listening
docker exec broker kafka-broker-api-versions.sh --bootstrap-server localhost:9092

# Check ZooKeeper connection
docker compose logs zookeeper
```

**Producer unable to send messages**
```bash
# Verify topic exists
docker exec broker kafka-topics.sh --list --bootstrap-server localhost:9092

# Create topic if missing
docker exec broker kafka-topics.sh --create \
  --topic users_topic \
  --bootstrap-server localhost:9092 \
  --partitions 3 \
  --replication-factor 1
```

**Consumer lag growing**
- Check Spark processor is running
- Verify Spark job logs: `docker compose logs spark-master`
- Check for stuck tasks in Spark UI

---

### 5. Spark Issues

**Spark job fails to start**
```bash
# Check master logs
docker compose logs spark-master

# Verify master is accessible
docker exec spark-master curl http://localhost:7077/json/

# Check memory allocation
docker exec spark-master jps -l | grep Master
```

**Data not flowing from Kafka to database**
1. Verify Kafka has messages: 
   ```bash
   docker exec broker kafka-console-consumer.sh \
     --topic users_topic \
     --bootstrap-server localhost:9092 \
     --from-beginning | head -5
   ```

2. Check Spark job status:
   ```bash
   # Access Spark UI at localhost:4040
   docker compose logs spark-master | grep -i "task"
   ```

3. Verify database connectivity:
   ```bash
   # Test PostgreSQL
   docker exec postgres psql -U airflow -d airflow -c "SELECT 1;"
   
   # Test Cassandra
   docker exec cassandra cqlsh -e "SELECT * FROM system.local;"
   ```

---

### 6. Superset Issues

**Superset UI loads slowly**
- Wait longer (first load can take 2-3 minutes)
- Check available memory: `docker stats superset-app`
- Increase container resources if needed

**Superset cannot connect to databases**
```bash
# Verify database credentials in Superset settings
# Navigate to: Settings → Database Connections

# Test connection manually
docker exec postgres psql -h postgres -U airflow -d airflow -c "SELECT 1;"

# Check Superset logs
docker compose logs superset-app | grep -i "error\|connection"
```

**Dashboards not loading data**
- Verify data exists in database tables
- Check SQL query syntax in dataset editor
- Review query permissions for database user

---

### 7. Network Issues

**Services can't communicate (cross-container)**
```bash
# Check network
docker network ls
docker network inspect e2e_airflow-network

# Verify DNS resolution inside container
docker exec airflow-webserver ping postgres
docker exec airflow-webserver ping broker
```

**Port already in use**
```bash
# Find process using port
netstat -tuln | grep LISTEN

# Change port in docker-compose or environment
# Update .env file or compose file
```

---

### 8. Data Issues

**Data appearing duplicated**
- Check Kafka message retention
- Verify Spark job idempotency
- Review Cassandra TTL settings

**Missing data in Cassandra**
```bash
# Check table structure
docker exec cassandra cqlsh -e "DESCRIBE TABLE user_events;"

# Count rows
docker exec cassandra cqlsh -e "SELECT COUNT(*) FROM user_events;"

# Check replication
docker exec cassandra cqlsh -e "DESCRIBE KEYSPACE;"
```

---

## System Resource Troubleshooting

### Check Resources
```bash
# View container resource usage
docker stats

# Check system disk space
df -h

# Check system memory
free -h  # Linux
Get-ComputerInfo | Select-Object OSTotalVisibleMemorySize  # Windows
```

### Increase Resources
```bash
# Edit docker-compose.yml for service
services:
  postgres:
    # ... existing config ...
    deploy:
      resources:
        limits:
          memory: 2G
        reservations:
          memory: 1G
```

---

## Reset & Clean

**Soft reset (keep data)**
```bash
docker compose restart
```

**Hard reset (remove all containers)**
```bash
docker compose down
docker compose up -d
```

**Full reset (remove data volumes)**
```bash
docker compose down -v
docker compose up -d
```

**Complete system cleanup**
```bash
# Remove dangling images
docker image prune -f

# Remove unused networks
docker network prune -f

# Remove unused volumes
docker volume prune -f
```

---

## Getting Help

1. **Check logs first**
   ```bash
   docker compose logs service-name
   ```

2. **Search existing issues**
   - GitHub Issues
   - Stack Overflow
   - Service-specific documentation

3. **Create detailed issue report with:**
   - Error message/logs
   - Steps to reproduce
   - `docker compose ps` output
   - OS and Docker version

---

**Last Updated:** 2026-02-02
