#!/bin/bash

# Confluent Docker Entrypoint with Topic Creation

set -e

# Source Confluent configuration
. /etc/confluent/docker/bash-config.sh

# Start the Kafka broker in the background
/etc/confluent/docker/docker-entrypoint.sh &
BROKER_PID=$!

# Wait for Kafka broker to be ready
echo "Waiting for Kafka broker to be ready..."
for i in {1..60}; do
  if nc -z localhost 9092 2>/dev/null; then
    echo "Kafka broker is ready!"
    break
  fi
  echo "Waiting... (attempt $i/60)"
  sleep 1
done

# Give the broker a moment to fully initialize
sleep 2

# Run topic creation script if it exists
if [ -f /scripts/create_topic.sh ]; then
  echo "Running topic creation script..."
  chmod +x /scripts/create_topic.sh
  /scripts/create_topic.sh || echo "Topic creation script failed or completed with warnings"
else
  echo "Warning: /scripts/create_topic.sh not found"
fi

# Keep the broker running
wait $BROKER_PID

