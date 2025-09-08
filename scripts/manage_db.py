import argparse
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path="../.env")

DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")

def execute_sql(sql_path):
    with open(sql_path, "r") as f:
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
    print(f"Executed {sql_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "action",
        choices=["schema", "data"],
        help="Action to perform: 'schema' to create tables, 'data' to load sample data"
    )
    args = parser.parse_args()
    if args.action == "schema":
        execute_sql("../sql/schema.sql")
    elif args.action == "data":
        execute_sql("../sql/insert_sample_data.sql")

