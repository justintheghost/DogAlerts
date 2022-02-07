import requests
from bs4 import BeautifulSoup
from datetime import datetime
import os
from twilio.rest import Client
import psycopg2
from google.cloud import logging

def access_secret_version(secret_id, project_id="dogalert", version_id="latest"):
    """
    Access the payload for the given secret version if one exists. The version
    can be a version number as a string (e.g. "5") or an alias (e.g. "latest").
    """

    # Import the Secret Manager client library.
    from google.cloud import secretmanager

    # Create the Secret Manager client.
    client = secretmanager.SecretManagerServiceClient()

    # Build the resource name of the secret version.
    name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"

    # Access the secret version.
    response = client.access_secret_version(request={"name": name})

    payload = response.payload.data.decode("UTF-8")
    return payload



postgres_password = access_secret_version("postgres_password")
postgres_host = access_secret_version("postgres_host")

def execute_select_query(query):
    #establishing the connection
    conn = psycopg2.connect(
        database="postgres", user='postgres', password=postgres_password, host=postgres_host, port= '5432'
    )
    #Creating a cursor object using the cursor() method
    cursor = conn.cursor()

    #Executing an MYSQL function using the execute() method
    cursor.execute(query)
    data = cursor.fetchall()
    # print("Connection established to: ",data)
    conn.commit()
 
    conn.close()
    return data

def execute_multiple_row_insert(list):
    #establishing the connection
    conn = psycopg2.connect(
        database="postgres", user='postgres', password=postgres_password, host=postgres_host, port= '5432'
    )
    #Creating a cursor object using the cursor() method
    cursor = conn.cursor()

    #Executing an MYSQL function using the execute() method
    # cursor.execute(query)
    try:
        cursor.executemany("INSERT INTO dog_alerts.dogs VALUES(%s,%s,%s)", list)
    except Exception as e:
        print(e)
    # data = cursor.fetchone()
    # print("Connection established to: ",data)
    conn.commit()
 
    conn.close()

def log_event(message):
    logging_client = logging.Client()

    # The name of the log to write to
    log_name = "dog-alert-log"
    # Selects the log to write to
    logger = logging_client.logger(log_name)

    # Writes the log entry
    logger.log_text(message)


# def seed_database_with_animal_ids():
#     all_animals = get_all_animals()
#     all_animal_ids = get_all_animal_ids(all_animals)
#     #new_animal_id_list = identify_new_animal_ids(all_animals)
#     data = [(i, datetime.now(), datetime.now()) for i in all_animal_ids]
#     execute_multiple_row_insert(data)
