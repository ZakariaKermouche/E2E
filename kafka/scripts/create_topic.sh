#!/bin/bash

# Create Kafka Topics

set -e

# Set variables
BOOTSTRAP_SERVER="localhost:9092"
PARTITIONS=3
REPLICATION_FACTOR=1
RETENTION_MS=172800000  # 48 hours in milliseconds

# Use full path to Confluent tools
KAFKA_TOPICS="/usr/bin/kafka-topics"
KAFKA_CONFIGS="/usr/bin/kafka-configs"

# Array of topics to create
declare -A TOPICS=(
  [users_topic]="User data stream"
  [events_topic]="User events"
  [logs_topic]="Application logs"
)

echo ""
echo "=========================================="
echo "Creating Kafka topics..."
echo "Bootstrap Server: $BOOTSTRAP_SERVER"
echo "=========================================="
echo ""

for topic in "${!TOPICS[@]}"; do
  description="${TOPICS[$topic]}"
  echo "Creating topic: $topic ($description)"
  
  # Create topic if it doesn't exist
  $KAFKA_TOPICS --create \
    --bootstrap-server $BOOTSTRAP_SERVER \
    --topic $topic \
    --partitions $PARTITIONS \
    --replication-factor $REPLICATION_FACTOR \
    --if-not-exists 2>/dev/null || true
  
  # Set retention time to 48 hours
  $KAFKA_CONFIGS --bootstrap-server $BOOTSTRAP_SERVER \
    --alter \
    --entity-type topics \
    --entity-name $topic \
    --add-config retention.ms=$RETENTION_MS \
    2>/dev/null || true
  
  echo "✓ Topic $topic ready (retention: 48 hours)"
done

echo ""
echo "=========================================="
echo "Topic creation completed!"
echo "=========================================="
echo ""
echo "Existing topics:"
$KAFKA_TOPICS --list --bootstrap-server $BOOTSTRAP_SERVER
echo ""
