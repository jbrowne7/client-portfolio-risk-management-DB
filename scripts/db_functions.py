import psycopg2
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path="../.env")

DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")




# This function might not really be practical as a left join? Wanted to show usage / knowledge of left
# joins but I think every asset should have at least one price entry so not sure, this was the only
# idea I could think of for using left join at the moment. This problem is because most fields in my schema
# are required I think.
def get_assets_latest_price(conn):
    cur = conn.cursor()
    cur.execute("""
        SELECT a.asset_id, a.symbol, p.price_date, p.price
        FROM assets a
        LEFT JOIN prices p ON a.asset_id = p.asset_id AND p.price_date = (
            SELECT MAX(price_date) FROM prices WHERE asset_id = a.asset_id
        )
        ORDER BY a.asset_id;
    """)
    results = cur.fetchall()
    columns = [desc[0] for desc in cur.description]
    cur.close()
    return results, columns

def get_portfolios_with_clients(conn):
    cur = conn.cursor()
    cur.execute("""
        SELECT p.portfolio_id, c.name AS client_name
        FROM portfolios p
        INNER JOIN clients c ON p.client_id = c.client_id;
    """)
    results = cur.fetchall()
    columns = [desc[0] for desc in cur.description]
    cur.close()
    return results, columns

def get_recent_trades(conn, days=30):
    cur = conn.cursor()
    cur.execute("""
        SELECT *
        FROM trades
        WHERE trade_date >= NOW() - INTERVAL '%s days'
        ORDER BY trade_date DESC;
    """, (days,))
    results = cur.fetchall()
    columns = [desc[0] for desc in cur.description]
    cur.close()
    return results, columns

def get_top_portfolios_by_value(conn, limit=5):
    cur = conn.cursor()
    cur.execute("""
        SELECT p.portfolio_id, SUM(t.quantity * t.price) AS total_value
        FROM portfolios p
        JOIN trades t ON p.portfolio_id = t.portfolio_id
        GROUP BY p.portfolio_id
        ORDER BY total_value DESC
        LIMIT %s;
    """, (limit,))
    results = cur.fetchall()
    columns = [desc[0] for desc in cur.description]
    cur.close()
    return results, columns

def get_clients_with_no_trades(conn):
    cur = conn.cursor()
    cur.execute("""
        SELECT c.client_id, c.name
        FROM clients c
        WHERE c.client_id NOT IN (
            SELECT p.client_id
            FROM portfolios p
            JOIN trades t ON p.portfolio_id = t.portfolio_id
        )
    """)
    results = cur.fetchall()
    columns = [desc[0] for desc in cur.description]
    cur.close()
    return results, columns

def get_trade_counts_by_asset(conn):
    cur = conn.cursor()
    cur.execute("""
        SELECT asset_id, COUNT(*) AS trade_count
        FROM trades
        GROUP BY asset_id
        ORDER BY trade_count DESC;
    """)
    results = cur.fetchall()
    columns = [desc[0] for desc in cur.description]
    cur.close()
    return results, columns

def get_all_trades_for_asset_in_portfolio(conn, portfolio_id, asset_id):
    cur = conn.cursor()
    cur.execute("""
        SELECT *
        FROM trades
        WHERE portfolio_id = %s
            AND asset_id = %s
        ORDER BY trade_date;
    """, (portfolio_id, asset_id))
    results = cur.fetchall()
    columns = [desc[0] for desc in cur.description]
    cur.close()
    return results, columns

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
