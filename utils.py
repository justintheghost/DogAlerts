import requests
from bs4 import BeautifulSoup
from datetime import datetime
import os
from twilio.rest import Client
import psycopg2
from google.cloud import logging
import sqlalchemy

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
    log_event("Establishing connection...")
    conn = psycopg2.connect(
        database="postgres"
        , user='postgres'
        , password=postgres_password
        , host="/cloudsql/dogalert:us-central1:dog-alert-db"
        , port= '5432'
    )
    #Creating a cursor object using the cursor() method
    cursor = conn.cursor()

    #Executing an MYSQL function using the execute() method
    log_event("Execute query...")
    cursor.execute(query)

    log_event("Fetch data...")
    data = cursor.fetchall()
    # print("Connection established to: ",data)
    log_event("Commit transaction...")
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

def run_sql():
    pool = sqlalchemy.create_engine(

    # Equivalent URL:
    # postgresql+pg8000://<db_user>:<db_pass>@/<db_name>
    #                         ?unix_sock=<socket_path>/<cloud_sql_instance_name>/.s.PGSQL.5432
    # Note: Some drivers require the `unix_sock` query parameter to use a different key.
    # For example, 'psycopg2' uses the path set to `host` in order to connect successfully.
    sqlalchemy.engine.URL.create(
        drivername="postgresql",
        username="postgres",  # e.g. "my-database-user"
        password=postgres_password,  # e.g. "my-database-password"
        database="postgres",  # e.g. "my-database-name"
        query={
            "unix_sock": "{}/{}/.s.PGSQL.5432".format(
                "/cloudsql",  # e.g. "/cloudsql"
                "dogalert:us-central1:dog-alert-db")  # i.e "<PROJECT-NAME>:<INSTANCE-REGION>:<INSTANCE-NAME>"
        }
    )
)
# def seed_database_with_animal_ids():
#     all_animals = get_all_animals()
#     all_animal_ids = get_all_animal_ids(all_animals)
#     #new_animal_id_list = identify_new_animal_ids(all_animals)
#     data = [(i, datetime.now(), datetime.now()) for i in all_animal_ids]
#     execute_multiple_row_insert(data)
