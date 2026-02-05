# # Get data from kafka and process with Spark Streaming and send them to cassandra
# from datetime import datetime
# from cassandra.cluster import Cluster
# from pyspark.sql import SparkSession
# from pyspark.sql.functions import from_json, col
# from pyspark.sql.types import StructType, StructField, StringType, IntegerType, TimestampType


# # Create keyspace 

# def create_keyspace(sessio):
#     sessio.execute("""
#     CREATE KEYSPACE IF NOT EXISTS user_data
#     WITH REPLICATION = { 'class' : 'SimpleStrategy', 'replication_factor' : 1 }
#     """)
    
#     print("Keyspace created or already exists.")


# # Table creation
# def create_table(session):
#     session.execute("""
#     CREATE TABLE IF NOT EXISTS user_data.users (
#         id UUID PRIMARY KEY,
#         first_name text,
#         last_name text,
#         gender text,
#         email text,
#         dob timestamp,
#         age int,
#         phone text,
#         cell text,
#         nationality text,
#         picture text,
#         address text,
#         postcode text
#         """)

#     print("Table created or already exists.")


# # Data insertion
# def insert_data(session, data):
#     insert_query = """
#     INSERT INTO user_data.users (id, 
#     first_name, 
#     last_name, 
#     gender, 
#     email, 
#     dob,
#     age,
#     phone,
#     cell,
#     nationality,
#     picture,
#     address,
#     postcode)
#     VALUES (uuid(), %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
#     """
#     session.execute(insert_query, (
#         data['first_name'],
#         data['last_name'],
#         data['gender'],
#         data['email'], 
#         data['dob'],    
#         data['age'],
#         data['phone'],
#         data['cell'],
#         data['nationality'],
#         data['picture'],
#         data['address'],
#         data['postcode']
#     ))
#     print("Data inserted into Cassandra:", data['first_name'], data['last_name']) 


# # create_spark_connection 
# def create_spark_connection():
#     conn = None

#     try:
#         spark = SparkSession \
#             .builder \
#             .appName("KafkaSparkCassandra") \
#             .config("spark.jars.packages", "com.datastax.spark:spark-cassandra-connector_2.13:3.5.1,org.apache.spark:spark-sql-kafka-0-10_2.13:4.1.1") \
#             .config("spark.cassandra.connection.host", "localhost") \
#             .getOrCreate()
#         spark.sparkContext.setLogLevel("ERROR")
#         conn = spark

#         print("Spark session created successfully.")
#     except Exception as e:
#         print("Error creating Spark session:", e)
#     return conn



# # connect_to_kafka
# def connect_to_kafka(spark):
#     spark_df = None

#     try:
#         spark_df = spark \
#             .readStream \
#             .format("kafka") \
#             .option("kafka.bootstrap.servers", "broker:29092") \
#             .option("subscribe", "users") \
#             .option("startingOffsets", "earliest") \
#             .load()
#         print("Connected to Kafka successfully.")
#     except Exception as e:
#         print("Error connecting to Kafka:", e)

#     return spark_df



# # create_cassandra_connection
# def create_cassandra_connection():
#     try:
#         cluster = Cluster(['cassandra'])
#         session = cluster.connect()
#         print("Connected to Cassandra successfully.")
#         return session
#     except Exception as e:
#         print("Error connecting to Cassandra:", e)
#         return None
    

# # create_selection_df_from_kafka
# def create_selection_df_from_kafka(spark_df):
#     schema = StructType([
#         StructField("first_name", StringType(), True),
#         StructField("last_name", StringType(), True),
#         StructField("gender", StringType(), True),
#         StructField("email", StringType(), True), 
#         StructField("dob", TimestampType(), True),
#         StructField("age", IntegerType(), True),
#         StructField("phone", StringType(), True),
#         StructField("cell", StringType(), True),
#         StructField("nationality", StringType(), True),
#         StructField("picture", StringType(), True),
#         StructField("address", StringType(), True),
#         StructField("postcode", StringType(), True)
#     ])

#     selection_df = spark_df.selectExpr("CAST(value AS STRING) as json_value") \
#         .select(from_json(col("json_value"), schema).alias("data")) \
#         .select("data.*")
#     return selection_df



# # if __name__ == "__main__":

# if __name__ == "__main__":
#     # create spark connection
#     spark = create_spark_connection()

#     if spark is not None:
#         # connect to kafka
#         spark_df = connect_to_kafka(spark)

#         if spark_df is not None:
#             # create cassandra connection
#             cassandra_session = create_cassandra_connection()

#             if cassandra_session is not None:
#                 # create keyspace and table
#                 create_keyspace(cassandra_session)
#                 create_table(cassandra_session)

#                 # create selection df from kafka
#                 selection_df = create_selection_df_from_kafka(spark_df)

#                 # write to cassandra
#                 query = selection_df.writeStream \
#                     .foreachBatch(lambda df, epochId: df.foreach(lambda row: insert_data(cassandra_session, row.asDict()))) \
#                     .outputMode("update") \
#                     .start()
#                 query.awaitTermination()
#                 print("Streaming data from Kafka to Cassandra...")
#             else:
#                 print("Cassandra connection not established.")
#         else:
#             print("Kafka connection not established.")
#     else:
#         print("Spark connection not established.")


import logging

from cassandra.cluster import Cluster
from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import StructType, StructField, StringType

import os
os.environ['PYSPARK_SUBMIT_ARGS'] = '--packages org.apache.spark:spark-sql-kafka-0-10_2.13:4.0.0,com.datastax.spark:spark-cassandra-connector_2.13:3.5.1 pyspark-shell'



def create_keyspace(session):
    session.execute("""
        CREATE KEYSPACE IF NOT EXISTS spark_streams
        WITH replication = {'class': 'SimpleStrategy', 'replication_factor': '1'};
    """)

    print("Keyspace created successfully!")


def create_table(session):
    session.execute("""
    CREATE TABLE IF NOT EXISTS spark_streams.created_users (
        id UUID PRIMARY KEY,
        first_name TEXT,
        last_name TEXT,
        gender TEXT,
        address TEXT,
        post_code TEXT,
        email TEXT,
        username TEXT,
        registered_date TEXT,
        phone TEXT,
        picture TEXT);
    """)

    print("Table created successfully!")


def insert_data(session, **kwargs):
    print("inserting data...")

    user_id = kwargs.get('id')
    first_name = kwargs.get('first_name')
    last_name = kwargs.get('last_name')
    gender = kwargs.get('gender')
    address = kwargs.get('address')
    postcode = kwargs.get('post_code')
    email = kwargs.get('email')
    username = kwargs.get('username')
    dob = kwargs.get('dob')
    registered_date = kwargs.get('registered_date')
    phone = kwargs.get('phone')
    picture = kwargs.get('picture')

    try:
        session.execute("""
            INSERT INTO spark_streams.created_users(id, first_name, last_name, gender, address, 
                post_code, email, username, dob, registered_date, phone, picture)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (user_id, first_name, last_name, gender, address,
              postcode, email, username, dob, registered_date, phone, picture))
        logging.info(f"Data inserted for {first_name} {last_name}")

    except Exception as e:
        logging.error(f'could not insert data due to {e}')


def create_spark_connection():
    s_conn = None

    try:
        s_conn = SparkSession.builder \
            .appName('SparkDataStreaming') \
            .config('spark.jars.packages', "com.datastax.spark:spark-cassandra-connector_2.13:3.5.1,"
                                           "org.apache.spark:spark-sql-kafka-0-10_2.13:4.1.1") \
            .config('spark.cassandra.connection.host', 'cassandra') \
            .getOrCreate()

        s_conn.sparkContext.setLogLevel("ERROR")
        logging.info("Spark connection created successfully!")
    except Exception as e:
        logging.error(f"Couldn't create the spark session due to exception {e}")

    return s_conn


def connect_to_kafka(spark_conn):
    spark_df = None
    try:
        spark_df = spark_conn.readStream \
            .format('kafka') \
            .option('kafka.bootstrap.servers', 'broker:29092') \
            .option('subscribe', 'users_created') \
            .option('startingOffsets', 'earliest') \
            .load()
        logging.info("kafka dataframe created successfully")
    except Exception:
        # Log full exception and stack for debugging
        logging.exception("Kafka dataframe could not be created")
        # Re-raise to fail-fast so the app doesn't continue with None
        raise

    if spark_df is None:
        raise RuntimeError("Failed to create Kafka DataFrame: spark_df is None")

    return spark_df


def create_cassandra_connection():
    try:
        # connecting to the cassandra cluster
        cluster = Cluster(['cassandra'])

        cas_session = cluster.connect()

        return cas_session
    except Exception as e:
        logging.error(f"Could not create cassandra connection due to {e}")
        return None


def create_selection_df_from_kafka(spark_df):
    schema = StructType([
        StructField("id", StringType(), False),
        StructField("first_name", StringType(), False),
        StructField("last_name", StringType(), False),
        StructField("gender", StringType(), False),
        StructField("address", StringType(), False),
        StructField("post_code", StringType(), False),
        StructField("email", StringType(), False),
        StructField("username", StringType(), False),
        StructField("registered_date", StringType(), False),
        StructField("phone", StringType(), False),
        StructField("picture", StringType(), False)
    ])

    sel = spark_df.selectExpr("CAST(value AS STRING)") \
        .select(from_json(col('value'), schema).alias('data')).select("data.*")
    print(sel)

    return sel


if __name__ == "__main__":
    # create spark connection
    spark_conn = create_spark_connection()

    if spark_conn is not None:
        # connect to kafka with spark connection
        spark_df = connect_to_kafka(spark_conn)
        selection_df = create_selection_df_from_kafka(spark_df)
        session = create_cassandra_connection()

        if session is not None:
            create_keyspace(session)
            create_table(session)

            logging.info("Streaming is being started...")

            streaming_query = (selection_df.writeStream.format("org.apache.spark.sql.cassandra")
                               .option('checkpointLocation', '/tmp/checkpoint')
                               .option('keyspace', 'spark_streams')
                               .option('table', 'created_users')
                               .start())

            streaming_query.awaitTermination()