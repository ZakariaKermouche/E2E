from datetime import datetime
import time
from airflow import DAG
from airflow.sdk import dag, task, task_group
from airflow.providers.standard.operators.python import PythonOperator

default_args = {
    'owner': 'Airflow',
    'start_date': datetime(2021, 1, 1),
    'depends_on_past': False,
}

def get_data():

    import requests

    url= 'https://randomuser.me/api/'
    response = requests.get(url)
    response = response.json()
    results = response['results'][0]

    return results


def format_data(res):


    data = {}
    data['first_name'] = res['name']['first']
    data['last_name'] = res['name']['last']
    data['gender'] = res['gender']
    data['email'] = res['email']
    data['dob'] = res['dob']['date']  # or parse to datetime if needed
    data['age'] = res['dob']['age']
    data['phone'] = res['phone']
    data['cell'] = res['cell']
    data['nationality'] = res['nat']
    data['picture'] = res['picture']['large']
    data['address'] = f"{res['location']['street']['number']} {res['location']['street']['name']}, {res['location']['city']}, {res['location']['state']}, {res['location']['country']}"

    data['postcode'] = res['location']['postcode']
    data['created_date'] = datetime.now().isoformat()
    data['year'] = datetime.now().isoformat().split('T')[0].split('-')[0]
    data['month'] = datetime.now().isoformat().split('T')[0].split('-')[1]
    data['day'] = datetime.now().isoformat().split('T')[0].split('-')[2]

    return data

# @task
def stream_data():

    import json
    from kafka import KafkaProducer
    import time
    import logging
    try:
        producer = KafkaProducer(bootstrap_servers=['broker:29092'], max_block_ms=5000
                                ,
            api_version=(0, 10, 1))

        res = get_data()
        res = format_data(res)
        print("Sending data to Kafka:", res)
        producer.send('users_created', json.dumps(res).encode('utf-8'))
    
    except Exception as e:
        logging.error(f'An error occurred: {e}')
    # curr_time = time.time()

    # while True:
    #     if time.time() > curr_time + 60: #1 minute
    #         break
    #     try:
    #        print("Getting data...")
            
    #     except Exception as e:
    #         logging.error(f'An error occured: {e}')
    #         continue
    return "done"
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
    schedule='@daily',
    catchup=False,
) as dag:
    stream_task = PythonOperator(
        task_id='stream',
        python_callable=stream_data,
        
    )

stream_data()