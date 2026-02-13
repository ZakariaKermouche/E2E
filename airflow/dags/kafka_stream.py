from datetime import datetime, timedelta
import time
from airflow import DAG
from airflow.sdk import dag, task, task_group
from airflow.providers.standard.operators.python import PythonOperator

default_args = {
    'owner': 'Airflow',
    'start_date': datetime(2021, 1, 1),
    'depends_on_past': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=1),
}

def get_data():

    
    import random
    import uuid

    first_names = ["Liam", "Noah", "Emma", "Olivia", "Mia", "Lucas", "Yasmine", "Amir", "Sofia", "Adam"]
    last_names = ["Smith", "Johnson", "Brown", "Davis", "Garcia", "Miller", "Wilson", "Anderson", "Thomas", "Martin"]
    streets = ["Main St", "Oak Ave", "Pine Rd", "Maple Dr", "Cedar Ln", "Elm St"]
    cities = ["Paris", "Lyon", "Marseille", "Toulouse", "Bordeaux", "Nice"]
    domains = ["example.com", "mail.com", "test.org", "demo.net"]

    first_name = random.choice(first_names)
    last_name = random.choice(last_names)
    username = f"{first_name.lower()}.{last_name.lower()}{random.randint(10, 999)}"
    email = f"{username}@{random.choice(domains)}"

    now = datetime.utcnow()
    return {
        'id': str(uuid.uuid4()),
        'first_name': first_name,
        'last_name': last_name,
        'gender': random.choice(['male', 'female']),
        'address': f"{random.randint(1, 999)} {random.choice(streets)}, {random.choice(cities)}",
        'post_code': f"{random.randint(10000, 99999)}",
        'email': email,
        'username': username,
        'registered_date': now.isoformat() + 'Z',
        'phone': f"+33{random.randint(600000000, 799999999)}",
        'picture': f"https://picsum.photos/seed/{username}/200/200",
    }

    # For real API call, uncomment below and comment out the above code
    #import requests

    # url= 'https://randomuser.me/api/'
    # response = requests.get(url)
    # response = response.json()
    # results = response['results'][0]
    # response = requests.get(url, timeout=10)
    
    # response.raise_for_status()
    # payload = response.json()
    # results = payload.get('results') or []

  
    # if not results:
    #     raise ValueError(f"randomuser response has no results: {payload}")

    # return results[0]



def format_data(res):

    return res

    # Used with real API response, not with generated data


    # data = {}
    # data['first_name'] = res['name']['first']
    # data['last_name'] = res['name']['last']
    # data['gender'] = res['gender']
    # data['email'] = res['email']
    # data['dob'] = res['dob']['date']  # or parse to datetime if needed
    # data['age'] = res['dob']['age']
    # data['phone'] = res['phone']
    # data['cell'] = res['cell']
    # data['nationality'] = res['nat']
    # data['picture'] = res['picture']['large']
    # data['address'] = f"{res['location']['street']['number']} {res['location']['street']['name']}, {res['location']['city']}, {res['location']['state']}, {res['location']['country']}"

    # data['postcode'] = res['location']['postcode']
    # data['created_date'] = datetime.now().isoformat()
    # data['year'] = datetime.now().isoformat().split('T')[0].split('-')[0]
    # data['month'] = datetime.now().isoformat().split('T')[0].split('-')[1]
    # data['day'] = datetime.now().isoformat().split('T')[0].split('-')[2]

    # return data

# @task
def stream_data():

    import json
    from kafka import KafkaProducer
    # import time
    import logging

    producer = None
    try:
        producer = KafkaProducer(
            bootstrap_servers=['broker:29092'],
            max_block_ms=5000,
            api_version=(0, 10, 1)
        )
 
        res = format_data(get_data())
        logging.info("Sending data to Kafka: %s", res)
 
    # producer.send('users', json.dumps(res).encode('utf-8'))
        future = producer.send('users_created', json.dumps(res).encode('utf-8'))
        future.get(timeout=10)
        producer.flush()
        return "done"
 
    except Exception:
        logging.exception('An error occurred while producing user data to Kafka')
        raise
    finally:
        if producer is not None:
            producer.close()
    # try:
    #     producer = KafkaProducer(bootstrap_servers=['broker:29092'], max_block_ms=5000
    #                             ,
    #         api_version=(0, 10, 1))

    #     res = get_data()
    #     res = format_data(res)
    #     print("Sending data to Kafka:", res)
    #     producer.send('users_created', json.dumps(res).encode('utf-8'))
    
    # except Exception as e:
    #     logging.error(f'An error occurred: {e}')


    # curr_time = time.time()

    # while True:
    #     if time.time() > curr_time + 60: #1 minute
    #         break
    #     try:
    #        print("Getting data...")
            
    #     except Exception as e:
    #         logging.error(f'An error occured: {e}')
    #         continue
    # return "done"
    # import json
    # from kafka import KafkaProducer

   

    # # print(json.dumps(res, indent=4))

    # producer = KafkaProducer(
    #     bootstrap_servers=['broker:29092'], 
    #     max_block_ms=5000,
    #     api_version=(0, 10, 1)
    # )


    # curr_time = time.time()

    # while True:
    #     # One minute of data streaming
    #     if time.time() - curr_time > 60:
    #         break
    #     try:
    #         res = get_data()
    #         res = format_data(res)
    #         producer.send('users', json.dumps(res).encode('utf-8'))
    #         print("Sent data to Kafka:", res)
            
    #     except Exception as e:
    #         print("Error sending data to Kafka:", e)
    #         continue


    # producer.send('users', json.dumps(res).encode('utf-8'))




with DAG(
    dag_id='kafka_stream',
    default_args=default_args,
    # schedule='@daily',
    schedule=timedelta(minutes=1),
    catchup=False,
    is_paused_upon_creation=False,
) as dag:
    stream_task = PythonOperator(
        task_id='stream',
        python_callable=stream_data,
        
    )

stream_data()