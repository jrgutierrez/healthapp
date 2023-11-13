import os
from dotenv import load_dotenv
import pymssql
from datetime import datetime

try:
    load_dotenv('.env')
except:
    pass

def connect_db():

    server = os.getenv('SERVER')
    database = os.getenv('DATABASE')
    username = os.getenv('USERNAME')
    password = os.getenv('PASSWORD')

    conn = pymssql.connect(
        server,
        username,
        password,
        database,
        as_dict=True
    )  

    return conn

def insert_user(username, name, lastname, gender, password):
    '''Returns 0: User already exists. 1: User created succesfully. 2: Error creating user'''
    if username in [user['username'] for user in fetch_all_users()]: return 0
    try:
        conn = connect_db()
        with conn.cursor() as cursor:
            query = f"INSERT INTO users_auth (username, name, lastname, gender, password) VALUES ('{username}', '{name}', '{lastname}', '{gender[0]}', '{password}');"
            cursor.execute(query)
            conn.commit()
    except:
        return 2
    return 1

def fetch_all_users():
    with connect_db().cursor() as cursor:
        query = "SELECT * FROM users_auth;"
        cursor.execute(query)
        return cursor.fetchall()
    
def get_user(username):
    with connect_db().cursor() as cursor:
        query = f"SELECT * FROM users_auth WHERE username='{username}';"
        cursor.execute(query)
        return cursor.fetchall()
    
def delete_user(username):
    conn = connect_db()
    with conn.cursor() as cursor:
        query = f"DELETE FROM users_auth WHERE username='{username}';"
        cursor.execute(query)
        conn.commit()

def create_user(username, name, lastname, gender, password):
    '''Returns 0: User already exists. 1: User created succesfully. 2: Error creating user. 3: Error inserting user in customers'''
    insert_result = insert_user(username, name, lastname, gender, password)
    if insert_result != 1: return insert_result
    try:
        conn = connect_db()
        with conn.cursor() as cursor:
            query = f"INSERT INTO dim_customers (username) VALUES ('{username}');"
            cursor.execute(query)
            conn.commit()
    except: return 3
    return 1

def get_user_data(username):
    with connect_db().cursor() as cursor:
        query = f"SELECT fh.* FROM fact_health fh INNER JOIN dim_customers dc on fh.customer_id = dc.customer_id WHERE dc.username='{username}';"
        cursor.execute(query)
        return cursor.fetchall()
    
def insert_data(username, weight, fat_perc, bone_mass, muscle_mass, date = None):
    '''Returns 0: User does not exist. 1: Data inserted succesfully. 2: Error getting customer id. 3: Error writting data.'''
    if username not in [user['username'] for user in fetch_all_users()]: return 0
    
    try:
        conn = connect_db()
        with conn.cursor() as cursor:
            query = f"SELECT * FROM dim_customers WHERE username='{username}';"
            cursor.execute(query)
            customer_id = cursor.fetchall()[0].get('customer_id')
    except: return 2
    
    try:
        if date is None:
            date = datetime.strftime(datetime.utcnow(), '%m/%d/%Y %H:%M')
        conn = connect_db()
        with conn.cursor() as cursor:
            query = f"""INSERT INTO fact_health (customer_id, date, weight, fat_perc, bone_mass, muscle_mass) 
                        VALUES ('{customer_id}', '{date}', '{weight}', '{fat_perc}', '{bone_mass}', '{muscle_mass}');"""
            cursor.execute(query)
            conn.commit()
    except: return 3

    return 1

def fetch_all_users_preauth():
    with connect_db().cursor() as cursor:
        query = "SELECT * FROM users_preauth;"
        cursor.execute(query)
        return cursor.fetchall()
    
def create_preauth_user(username):
    '''Returns 0: User already exists. 1: User created succesfully. 2: User already preauthorized. 3: Error creating user'''
    if username in [user['username'] for user in fetch_all_users()]: return 0
    if username in [user['username'] for user in fetch_all_users_preauth()]: return 2
    try:
        conn = connect_db()
        with conn.cursor() as cursor:
            query = f"INSERT INTO users_preauth (username) VALUES ('{username}');"
            cursor.execute(query)
            conn.commit()
    except:
        return 3
    return 1

def delete_preauth_user(username):
    conn = connect_db()
    with conn.cursor() as cursor:
        query = f"DELETE FROM users_preauth WHERE username='{username}';"
        cursor.execute(query)
        conn.commit()