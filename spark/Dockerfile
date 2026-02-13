FROM python:3.9-slim-bullseye

USER root

# Install Java and other dependencies (OpenJDK and Python are required for Spark) and requirements.txt
RUN apt-get update && apt-get install -y --no-install-recommends \
    openjdk-11-jre-headless \
    wget \
    curl \
    vim \
    procps \
    net-tools \
    iputils-ping \
    && rm -rf /var/lib/apt/lists/* 


# Set environment variables for Spark
ENV SPARK_VERSION=3.5.1 
ENV HADOOP_VERSION=3
ENV SPARK_HOME=/opt/spark
ENV PATH=$SPARK_HOME/bin:$PATH

# Clearly declare the Python version for Spark
ENV PYTHON_VERSION=3.9
ENV PYSPARK_DRIVER_PYTHON=python3

# Copy and install Python dependencies
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Download and install Spark

RUN curl -L https://archive.apache.org/dist/spark/spark-${SPARK_VERSION}/spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}.tgz -o spark.tgz && \
       tar -xf spark.tgz && \
       mv spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION} $SPARK_HOME && \
       rm spark.tgz

# Set the working directory
WORKDIR $SPARK_HOME/jars

# Jar files for Spark, Kafka, Cassandra
# RUN wget -q https://repo1.maven.org/maven2/org/apache/spark/spark-sql-kafka-0-10_2.12/${SPARK_VERSION}/spark-sql-kafka-0-10_2.12-${SPARK_VERSION}.jar && \
#     wget -q https://repo1.maven.org/maven2/org/apache/spark/spark-streaming-kafka-0-10_2.12/${SPARK_VERSION}/spark-streaming-kafka-0-10_2.12-${SPARK_VERSION}.jar && \
#     # wget -q https://repo1.maven.org/maven2/com/datastax/spark/spark-cassandra-connector_2.12/3.5.1/spark-cassandra-connector_2.12-3.5.1.jar && \
#     wget -q https://repo1.maven.org/maven2/com/datastax/spark/spark-cassandra-connector-assembly_2.12/3.5.1/spark-cassandra-connector-assembly_2.12-3.5.1.jar && \
#     wget -q https://repo1.maven.org/maven2/org/apache/kafka/kafka-clients/3.5.1/kafka-clients-3.5.1.jar && \
#     wget -q https://repo1.maven.org/maven2/org/apache/spark/spark-streaming-kafka-0-10-assembly_2.12/3.5.1/spark-streaming-kafka-0-10-assembly_2.12-3.5.1.jar

RUN wget -q https://repo1.maven.org/maven2/org/apache/spark/spark-sql-kafka-0-10_2.12/${SPARK_VERSION}/spark-sql-kafka-0-10_2.12-${SPARK_VERSION}.jar && \
    wget -q https://repo1.maven.org/maven2/org/apache/spark/spark-token-provider-kafka-0-10_2.12/${SPARK_VERSION}/spark-token-provider-kafka-0-10_2.12-${SPARK_VERSION}.jar && \
    wget -q https://repo1.maven.org/maven2/org/apache/kafka/kafka-clients/3.5.1/kafka-clients-3.5.1.jar && \
    wget -q https://repo1.maven.org/maven2/org/apache/commons/commons-pool2/2.12.0/commons-pool2-2.12.0.jar && \
    wget -q https://repo1.maven.org/maven2/com/datastax/spark/spark-cassandra-connector-assembly_2.12/3.5.1/spark-cassandra-connector-assembly_2.12-3.5.1.jar
 

# Working directory of the App
WORKDIR $SPARK_HOME