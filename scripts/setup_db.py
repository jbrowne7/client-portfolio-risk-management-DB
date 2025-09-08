import psycopg2
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path="../.env")

DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")

def run_schema():
    with open("../sql/schema.sql", "r") as f:
        schema_sql = f.read()
    
    conn = psycopg2.connect(
        dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT
    )

    cur = conn.cursor()

    for statement_raw in schema_sql.split(";"):
        statement = statement_raw.strip()
        if statement:
            cur.execute(statement + ";")
    cur.close()
    conn.commit()
    conn.close()
    print("Database schema created")

if __name__ == "__main__":
    run_schema()

