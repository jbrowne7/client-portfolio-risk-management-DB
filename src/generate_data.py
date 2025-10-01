import random
from faker import Faker
from db_functions import get_connection

fake = Faker()

NUM_CLIENTS = 10
NUM_PORTFOLIOS = 15
NUM_ASSETS = 8
NUM_TRADES = 40
NUM_PRICES = 100

def generate_clients(conn, num):
    cur = conn.cursor()
    for _ in range(num):
        first_name = fake.first_name()
        last_name = fake.last_name()
        cur.execute("INSERT INTO clients (first_name, last_name) VALUES (%s, %s);", (first_name, last_name))
    conn.commit()
    cur.close()

def generate_portfolios(conn, num, client_ids):
    cur = conn.cursor()
    for _ in range(num):
        client_id = random.choice(client_ids)
        cash_balance = round(random.uniform(1000, 10000), 2)
        cur.execute("INSERT INTO portfolios (client_id, cash_balance) VALUES (%s, %s);", (client_id, cash_balance))
    conn.commit()
    cur.close()

def generate_assets(conn, num):
    cur = conn.cursor()
    asset_classes = ['Stock', 'Bond', 'Forex', 'Crypto']
    base_currencies = ['USD', 'EUR', 'GBP', 'JPY']
    for i in range(num):
        symbol = fake.unique.lexify(text='????').upper()
        asset_class = random.choice(asset_classes)
        base_currency = random.choice(base_currencies)
        cur.execute(
            "INSERT INTO assets (symbol, asset_class, base_currency) VALUES (%s, %s, %s);",
            (symbol, asset_class, base_currency)
        )
    conn.commit()
    cur.close()

def generate_trades(conn, num, portfolio_ids, asset_ids):
    cur = conn.cursor()
    for _ in range(num):
        portfolio_id = random.choice(portfolio_ids)
        asset_id = random.choice(asset_ids)
        trade_date = fake.date_time_this_year()
        side = random.choice(['BUY', 'SELL'])
        quantity = round(random.uniform(1, 100), 2)
        price = round(random.uniform(10, 500), 2)
        cur.execute(
            "INSERT INTO trades (portfolio_id, asset_id, trade_date, side, quantity, price) VALUES (%s, %s, %s, %s, %s, %s);",
            (portfolio_id, asset_id, trade_date, side, quantity, price)
        )
    conn.commit()
    cur.close()

def generate_prices(conn, num, asset_ids):
    cur = conn.cursor()
    for _ in range(num):
        asset_id = random.choice(asset_ids)
        price_date = fake.date_this_year()
        price = random.uniform(10, 200)
        cur.execute(
            "INSERT INTO prices (asset_id, price_date, price) VALUES (%s, %s, %s) ON CONFLICT DO NOTHING;",
            (asset_id, price_date, price)
        )
    conn.commit()
    cur.close()

def generate_asset_notes(conn, num_notes, asset_ids):
    cur = conn.cursor()
    for _ in range(num_notes):
        # Using this to randomly decide whether to link the note to an asset or leave it unlinked, 0.8 = 80%
        if random.random() < 0.8:  
            asset_id = random.choice(asset_ids)
        else:
            asset_id = None 
        note = fake.sentence(nb_words=10)
        cur.execute(
            "INSERT INTO asset_notes (asset_id, note) VALUES (%s, %s);",
            (asset_id, note)
        )
    conn.commit()
    cur.close()

if __name__ == "__main__":
    conn = get_connection()
    print("Generating clients...")
    generate_clients(conn, NUM_CLIENTS)
    cur = conn.cursor()
    cur.execute("SELECT client_id FROM clients;")
    client_ids = [row[0] for row in cur.fetchall()]
    cur.close()

    print("Generating portfolios...")
    generate_portfolios(conn, NUM_PORTFOLIOS, client_ids)
    cur = conn.cursor()
    cur.execute("SELECT portfolio_id FROM portfolios;")
    portfolio_ids = [row[0] for row in cur.fetchall()]
    cur.close()

    print("Generating assets...")
    generate_assets(conn, NUM_ASSETS)
    cur = conn.cursor()
    cur.execute("SELECT asset_id FROM assets;")
    asset_ids = [row[0] for row in cur.fetchall()]
    cur.close()

    print("Generating trades...")
    generate_trades(conn, NUM_TRADES, portfolio_ids, asset_ids)

    print("Generating prices...")
    generate_prices(conn, NUM_PRICES, asset_ids)

    print("Generating asset notes...")
    generate_asset_notes(conn, 20, asset_ids)

    conn.close()
    print("Sample data generation complete.")
