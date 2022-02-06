import requests
from bs4 import BeautifulSoup
from datetime import datetime
import os
from twilio.rest import Client
import psycopg2
import secrets

def execute_select_query(query):
    #establishing the connection
    conn = psycopg2.connect(
        database="postgres", user='postgres', password=secrets.postgres_password, host=secrets.postgres_host, port= '5432'
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
    # TO DO: Take password out of source control
    #establishing the connection
    conn = psycopg2.connect(
        database="postgres", user='postgres', password=secrets.postgres_password, host=secrets.postgres_host, port= '5432'
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
 

# def seed_database_with_animal_ids():
#     all_animals = get_all_animals()
#     all_animal_ids = get_all_animal_ids(all_animals)
#     #new_animal_id_list = identify_new_animal_ids(all_animals)
#     data = [(i, datetime.now(), datetime.now()) for i in all_animal_ids]
#     execute_multiple_row_insert(data)
