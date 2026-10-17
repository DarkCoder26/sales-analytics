import mysql.connector

def get_connection():
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="12345",
        database="sales_analytics"
    )
    return connection

conn = get_connection()

if conn.is_connected():
    print("MYSQL connection established")
conn.close()