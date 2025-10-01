import psycopg2
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join("..", ".env"))

DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")

def add_price(conn, asset_id, price, price_date=None):
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO prices (asset_id, price_date, price)
        VALUES (%s, COALESCE(%s, CURRENT_DATE), %s)
        RETURNING asset_id, price_date;
        """,
        (asset_id, price_date, price),
    )
    inserted_asset_id, inserted_date = cur.fetchone()
    conn.commit()
    cur.close()
    print(f"Added price for asset {inserted_asset_id} on {inserted_date}: {price}")
    return inserted_asset_id, inserted_date


def add_asset(conn, symbol, asset_class, base_currency):
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO assets (symbol, asset_class, base_currency)
        VALUES (%s, %s, %s)
        RETURNING asset_id;
        """,
        (symbol, asset_class, base_currency),
    )
    asset_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    print(f"Added asset '{symbol}' ({asset_class}, {base_currency}) with asset_id {asset_id}")
    return asset_id

def add_trade(conn, portfolio_id, asset_id, side, quantity, price, trade_date):
    if side not in ("BUY", "SELL"):
        raise ValueError("side must be 'BUY' or 'SELL'")
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO trades (portfolio_id, asset_id, trade_date, side, quantity, price)
        VALUES (%s, %s, COALESCE(%s, NOW()), %s, %s, %s)
        RETURNING trade_id;
        """,
        (portfolio_id, asset_id, trade_date, side, quantity, price),
    )
    trade_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    print(f"Added trade {trade_id}: {side} {quantity} @ {price} (portfolio {portfolio_id}, asset {asset_id})")
    return trade_id

def add_portfolio(conn, client_id, cash_balance=0):
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO portfolios (client_id, cash_balance)
        VALUES (%s, %s)
        RETURNING portfolio_id;
        """,
        (client_id, cash_balance),
    )
    portfolio_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    print(f"Added portfolio '{portfolio_id}' for client_id {client_id} (cash_balance={cash_balance})")
    return portfolio_id

def get_assets_with_possible_notes(conn):
    cur = conn.cursor()
    cur.execute("""
        SELECT a.asset_id, a.symbol, n.note_id, n.note
        FROM assets a
        LEFT JOIN asset_notes n ON a.asset_id = n.asset_id
        ORDER BY a.asset_id;
    """)
    results = cur.fetchall()
    columns = [desc[0] for desc in cur.description]
    cur.close()
    return results, columns

def get_notes_with_possible_assets(conn):
    cur = conn.cursor()
    cur.execute("""
        SELECT n.note_id, n.note, a.asset_id, a.symbol
        FROM asset_notes n
        RIGHT JOIN assets a ON n.asset_id = a.asset_id;
    """)
    results = cur.fetchall()
    columns = [desc[0] for desc in cur.description]
    cur.close()
    return results, columns

def get_all_assets_and_notes(conn):
    cur = conn.cursor()
    cur.execute("""
        SELECT a.asset_id, a.symbol, n.note_id, n.note
        FROM assets a
        FULL OUTER JOIN asset_notes n ON a.asset_id = n.asset_id;
    """)
    results = cur.fetchall()
    columns = [desc[0] for desc in cur.description]
    cur.close()
    return results, columns

def get_assets_latest_price(conn):
    cur = conn.cursor()
    cur.execute("""
        SELECT a.asset_id, a.symbol, p.price_date, p.price
        FROM assets a
        JOIN prices p ON a.asset_id = p.asset_id AND p.price_date = (
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
        SELECT p.portfolio_id, CONCAT(c.first_name, ' ', c.last_name) AS client_name
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
        SELECT c.client_id, CONCAT(c.first_name, ' ', c.last_name) AS client_name
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
    cur.execute("SELECT client_id, first_name, last_name, CONCAT(first_name, ' ', last_name) AS full_name FROM clients;")
    results = cur.fetchall()
    columns = [desc[0] for desc in cur.description]
    cur.close()
    return results, columns

def search_clients_by_name(conn, name):
    cur = conn.cursor()
    cur.execute("""
        SELECT client_id, first_name, last_name, CONCAT(first_name, ' ', last_name) AS full_name 
        FROM clients 
        WHERE CONCAT(first_name, ' ', last_name) ILIKE %s 
           OR first_name ILIKE %s 
           OR last_name ILIKE %s;
    """, (f"%{name}%", f"%{name}%", f"%{name}%"))
    results = cur.fetchall()
    columns = [desc[0] for desc in cur.description]
    cur.close()
    return results, columns

def add_client(conn, name):
    name_parts = name.strip().split(' ', 1)
    first_name = name_parts[0]
    last_name = name_parts[1] if len(name_parts) > 1 else ''
    
    cur = conn.cursor()
    cur.execute("INSERT INTO clients (first_name, last_name) VALUES (%s, %s) RETURNING client_id;", (first_name, last_name))
    client_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    print(f"Added client '{first_name} {last_name}' with client_id {client_id}")
    return client_id

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
