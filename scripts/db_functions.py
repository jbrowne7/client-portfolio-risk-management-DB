import psycopg2
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path="../.env")

DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")

def get_all_clients(conn):
    cur = conn.cursor()
    cur.execute("SELECT client_id, name FROM clients;")
    results = cur.fetchall()
    columns = [desc[0] for desc in cur.description]
    cur.close()
    return results, columns

def search_clients_by_name(conn, name):
    cur = conn.cursor()
    cur.execute("SELECT client_id, name FROM clients WHERE name ILIKE %s;", (f"%{name}%",))
    results = cur.fetchall()
    columns = [desc[0] for desc in cur.description]
    cur.close()
    return results, columns

def add_client(conn, name):
    cur = conn.cursor()
    cur.execute("INSERT INTO clients (name) VALUES (%s) RETURNING client_id;", (name,))
    client_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    print(f"Added client '{name}' with client_id {client_id}")

def get_percentage_invested(conn):
    cur = conn.cursor()
    cur.execute("""
            SELECT p.portfolio_id,
                ROUND(
                    (COALESCE(SUM(t.quantity * t.price), 0) /
                    (COALESCE(SUM(t.quantity * t.price), 0) + p.cash_balance)) * 100, 2
                ) AS percentage_invested

            FROM portfolios p
            LEFT JOIN trades t ON p.portfolio_id = t.portfolio_id
            GROUP BY p.portfolio_id, p.cash_balance;
            """)
    results = cur.fetchall()
    columns = [desc[0] for desc in cur.description]
    cur.close()
    return results, columns


def get_clients_with_portfolios(conn):
    cur = conn.cursor()
    cur.execute("""
        SELECT c.name AS client_name, p.portfolio_id
        FROM clients c
        JOIN portfolios p ON c.client_id = p.client_id;
    """)
    results = cur.fetchall()
    columns = [desc[0] for desc in cur.description]
    cur.close()
    return results, columns

def get_portfolio_total_values(conn):
    cur = conn.cursor()
    cur.execute("""
        SELECT p.portfolio_id, SUM(t.quantity * t.price) AS total_value
        FROM portfolios p
        JOIN trades t ON p.portfolio_id = t.portfolio_id
        GROUP BY p.portfolio_id;
    """)
    results = cur.fetchall()
    columns = [desc[0] for desc in cur.description]
    return results, columns

def load_sample_data(conn):
    with open("../sql/insert_sample_data.sql", "r") as f:
        schema_sql = f.read()
    
    cur = conn.cursor()

    for statement_raw in schema_sql.split(";"):
        statement = statement_raw.strip()
        if statement:
            cur.execute(statement + ";")
    cur.close()
    conn.commit()
    conn.close()

def create_tables(conn):
    with open("../sql/schema.sql", "r") as f:
        schema_sql = f.read()

    cur = conn.cursor()
    for statement_raw in schema_sql.split(";"):
        statement = statement_raw.strip()
        if statement:
            cur.execute(statement + ";")
    cur.close()
    conn.commit()
    conn.close()

def get_connection():
    return psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )