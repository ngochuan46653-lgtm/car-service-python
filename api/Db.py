import mysql.connector

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="830niewlovesYanfei@",
        database="CarServiceDB"
    )